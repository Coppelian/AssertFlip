#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert Agentless localization outputs + SWE-bench Verified metadata into a dataset
whose *keys/shape* strictly match the provided "9Refactor schema template".

Key ideas (per user rules):
- repo_root is always: /home/coppelia/program/manual_craft/tmp/{instance_id}/{project}
  where {project} is the immediate child directory inside instance folder.
- line_level_localization comes from agentless (file -> suspect_lines).
- localized_code is built by concatenating per-file slices:
    [start of <file>]
    <lineno>| <code>
    ...
    ... Code Truncated ...

  If suspect_lines non-empty: from min(suspect_lines) to max(suspect_lines)+TAIL_AFTER_MAX lines.
  If suspect_lines empty but file is in agentless suspect file list: first FALLBACK_HEAD lines (or whole file).
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional


LINE_RE = re.compile(r"\bline:\s*(\d+)\b", re.IGNORECASE)


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(path: Path) -> List[dict]:
    rows: List[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            rows.append(json.loads(ln))
    return rows


def infer_schema_keys(schema_template_path: Path) -> List[str]:
    """
    The schema template file can be:
      - JSON list of objects (common)
      - single JSON object
    We'll infer the key order from the first object (preserve insertion order).
    """
    obj = read_json(schema_template_path)
    if isinstance(obj, list):
        if not obj:
            raise ValueError(f"Schema template list is empty: {schema_template_path}")
        first = obj[0]
    elif isinstance(obj, dict):
        first = obj
    else:
        raise ValueError("Schema template must be a JSON object or list of objects.")
    if not isinstance(first, dict):
        raise ValueError("Schema template must contain JSON objects.")
    return list(first.keys())


def load_verified_index(verified_path: Optional[Path]) -> Dict[str, dict]:
    """
    Load SWE-bench Verified metadata from a local file, if provided.
    Supported:
      - JSONL: each line is a dict with at least instance_id
      - JSON: list[dict] or dict
    If not provided, returns empty dict (caller may fill with nulls or implement HF datasets lookup).
    """
    if verified_path is None:
        return {}
    if not verified_path.exists():
        raise FileNotFoundError(str(verified_path))

    if verified_path.suffix.lower() == ".jsonl":
        rows = read_jsonl(verified_path)
        idx = {}
        for r in rows:
            iid = r.get("instance_id") or r.get("id")
            if iid:
                idx[iid] = r
        return idx

    obj = read_json(verified_path)
    idx = {}
    if isinstance(obj, list):
        for r in obj:
            if not isinstance(r, dict):
                continue
            iid = r.get("instance_id") or r.get("id")
            if iid:
                idx[iid] = r
    elif isinstance(obj, dict):
        # could be mapping instance_id -> row, or a single row
        if "instance_id" in obj:
            idx[obj["instance_id"]] = obj
        else:
            # mapping
            for k, v in obj.items():
                if isinstance(v, dict):
                    idx[k] = v
    else:
        raise ValueError("Verified file must be JSON/JSONL containing dict rows.")
    return idx


def resolve_repo_root(instance_src_dir: Path) -> Path:
    """
    Per user's constraint: repo root is the immediate child directory.
    We still defensively pick the best candidate if multiple dirs exist.
    """
    if not instance_src_dir.exists():
        raise FileNotFoundError(f"Instance source dir not found: {instance_src_dir}")

    candidates = [p for p in instance_src_dir.iterdir() if p.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No project directory found under: {instance_src_dir}")

    # filter obvious non-repo dirs
    skip = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "env", "build", "dist"}
    filtered = [p for p in candidates if p.name not in skip]
    if filtered:
        candidates = filtered

    if len(candidates) == 1:
        return candidates[0]

    # score candidates
    def score_dir(d: Path) -> int:
        score = 0
        for marker in ["pyproject.toml", "setup.py", "setup.cfg", ".git", "requirements.txt", "Pipfile"]:
            if (d / marker).exists():
                score += 10
        # prefer common repo layouts
        if (d / "src").exists():
            score += 2
        if any((d / m).exists() for m in ["README.md", "README.rst"]):
            score += 2
        return score

    candidates.sort(key=lambda d: (-score_dir(d), d.name))
    return candidates[0]


def parse_agentless_locations(agentless_jsonl_paths: List[Path]) -> Tuple[Dict[str, Set[int]], Set[str]]:
    """
    Returns:
      file_to_lines: filename -> set(lines)
      suspect_files: set(filename)
    Supports multiple JSONL files (union).
    Expected keys (common agentless):
      - found_edit_locs: dict[filename] -> list[str] (strings containing "line: N")
      - found_files: list[str]
    If structures differ, we try best-effort parsing.
    """
    file_to_lines: Dict[str, Set[int]] = {}
    suspect_files: Set[str] = set()

    for p in agentless_jsonl_paths:
        if not p.exists():
            continue
        for rec in read_jsonl(p):
            # collect suspect files
            ff = rec.get("found_files")
            if isinstance(ff, list):
                for f in ff:
                    if isinstance(f, str) and f.strip():
                        suspect_files.add(f.strip())

            # parse edit locs
            fel = rec.get("found_edit_locs")
            if isinstance(fel, dict):
                for fname, locs in fel.items():
                    if not isinstance(fname, str) or not fname.strip():
                        continue
                    fname = fname.strip()
                    if fname not in file_to_lines:
                        file_to_lines[fname] = set()
                    # locs can be list[str], str, list[dict], dict...
                    if isinstance(locs, str):
                        locs_iter = [locs]
                    elif isinstance(locs, list):
                        locs_iter = locs
                    else:
                        locs_iter = [locs]

                    for item in locs_iter:
                        if isinstance(item, str):
                            for m in LINE_RE.finditer(item):
                                file_to_lines[fname].add(int(m.group(1)))
                        elif isinstance(item, dict):
                            # try common shapes: {"line": 12}, {"start_line":..,"end_line":..}
                            if "line" in item and isinstance(item["line"], int):
                                file_to_lines[fname].add(item["line"])
                            else:
                                sl = item.get("start_line")
                                el = item.get("end_line")
                                if isinstance(sl, int) and isinstance(el, int) and sl <= el:
                                    for ln in range(sl, el + 1):
                                        file_to_lines[fname].add(ln)
                        elif isinstance(item, int):
                            file_to_lines[fname].add(item)

            # fallback: other possible keys (rare)
            locs = rec.get("locations") or rec.get("results")
            if isinstance(locs, list):
                for item in locs:
                    if not isinstance(item, dict):
                        continue
                    fname = item.get("filename") or item.get("file") or item.get("path")
                    if not isinstance(fname, str) or not fname.strip():
                        continue
                    fname = fname.strip()
                    suspect_files.add(fname)
                    if fname not in file_to_lines:
                        file_to_lines[fname] = set()
                    lines = item.get("suspect_lines")
                    if isinstance(lines, list):
                        for ln in lines:
                            if isinstance(ln, int):
                                file_to_lines[fname].add(ln)

    # Ensure suspect_files includes at least the keys we have lines for
    for f in file_to_lines.keys():
        suspect_files.add(f)

    return file_to_lines, suspect_files


def build_line_level_localization(file_to_lines: Dict[str, Set[int]], suspect_files: Set[str]) -> List[dict]:
    """
    Output list sorted by filename for deterministic results.
    Include entries for files with empty suspect lines if they appear in suspect_files.
    """
    all_files = sorted(suspect_files)
    out: List[dict] = []
    for f in all_files:
        lines = sorted(file_to_lines.get(f, set()))
        out.append({"filename": f, "suspect_lines": lines})
    return out


def safe_read_lines(path: Path) -> List[str]:
    # Preserve line endings stripped; localized_code is line-oriented and adds '\n' back.
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def build_localized_code(
    repo_root: Path,
    line_level_localization: List[dict],
    tail_after_max: int = 100,
    fallback_head: int = 500,
) -> str:
    """
    Concatenate per-file chunks.
    """
    parts: List[str] = []
    for entry in line_level_localization:
        filename = entry.get("filename")
        suspect_lines = entry.get("suspect_lines") or []
        if not isinstance(filename, str) or not filename:
            continue

        parts.append(f"[start of {filename}]\n")

        abs_path = repo_root / filename
        if not abs_path.exists() or not abs_path.is_file():
            # Deterministic placeholder
            parts.append(f"1| <MISSING FILE: {filename}>\n")
            parts.append("... Code Truncated ...\n\n")
            continue

        lines = safe_read_lines(abs_path)
        n = len(lines)

        if suspect_lines:
            # 1-based line numbers in output
            start = max(1, int(min(suspect_lines)))
            end = min(n, int(max(suspect_lines)) + int(tail_after_max))
        else:
            start = 1
            end = min(n, int(fallback_head))

        for lineno in range(start, end + 1):
            text = lines[lineno - 1]
            parts.append(f"{lineno}| {text}\n")

        parts.append("... Code Truncated ...\n\n")

    return "".join(parts)


def compose_row(schema_keys: List[str], verified_row: dict, instance_id: str,
                line_level_localization: List[dict], localized_code: str) -> dict:
    """
    Create an output dict that has exactly schema_keys keys, in that order.
    Fill from verified_row where possible, else null/empty.
    Then override localization fields.
    """
    out = {}
    for k in schema_keys:
        if k in ("line_level_localization", "localized_code"):
            # fill later
            out[k] = [] if k == "line_level_localization" else ""
            continue

        if k == "instance_id":
            out[k] = instance_id
            continue

        if verified_row is not None and k in verified_row:
            out[k] = verified_row[k]
        else:
            # sensible defaults
            if k in ("FAIL_TO_PASS", "PASS_TO_PASS"):
                out[k] = []
            else:
                out[k] = None

    # override
    out["localized_code"] = localized_code
    out["line_level_localization"] = line_level_localization
    # out["localized_code"] = localized_code
    # ensure instance_id present even if schema uses different naming
    if "instance_id" in out and out["instance_id"] is None:
        out["instance_id"] = instance_id
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True, type=Path, help="Path to ids.json")
    ap.add_argument("--schema_template", required=True, type=Path,
                    help="Path to 9Refactor schema template JSON (used for keys only)")
    ap.add_argument("--agentless_root", required=True, type=Path,
                    help="Root directory containing agentless outputs (raw_agentless style)")
    ap.add_argument("--source_root", required=True, type=Path,
                    help="Root directory containing local instance source folders (manual_craft/tmp)")
    ap.add_argument("--verified_path", type=Path, default=None,
                    help="Optional local SWE-bench Verified JSON/JSONL file to avoid HF download")
    ap.add_argument("--merged_mode", choices=["latest", "all"], default="latest",
                    help="latest: use the loc_merged_* file with the highest sort key; all: union all loc_merged_*_outputs.jsonl files found")
    ap.add_argument("--tail_after_max", type=int, default=100)
    ap.add_argument("--fallback_head", type=int, default=500)
    ap.add_argument("--out_json", required=True, type=Path, help="Output JSON (list)")
    ap.add_argument("--out_jsonl", type=Path, default=None, help="Optional output JSONL")
    args = ap.parse_args()

    ids_obj = read_json(args.ids)
    if isinstance(ids_obj, list):
        instance_ids = [str(x) for x in ids_obj]
    elif isinstance(ids_obj, dict) and "ids" in ids_obj and isinstance(ids_obj["ids"], list):
        instance_ids = [str(x) for x in ids_obj["ids"]]
    else:
        raise ValueError("ids.json must be a list of instance_ids or a dict with key 'ids'.")

    schema_keys = infer_schema_keys(args.schema_template)
    verified_idx = load_verified_index(args.verified_path)

    out_rows: List[dict] = []

    for iid in instance_ids:
        # --- agentless paths ---
        inst_dir = args.agentless_root / iid
        paths: List[Path] = []

        # Preferred: edit_location_merged
        merged_dir = inst_dir / "edit_location_merged"
        if merged_dir.exists():
            merged_files = sorted(merged_dir.glob("loc_merged_*_outputs.jsonl"))
        else:
            merged_files = []

        if args.merged_mode == "all":
            # Union across *all* loc_merged_*_outputs.jsonl files present (more or fewer than 4 is OK)
            paths.extend(merged_files)
        else:
            # "latest": pick the merged file with the highest sort key.
            # We avoid hard-coding counts; if multiple exist, prefer the one with the largest numeric tuple in its name.
            def _key(p: Path):
                m = re.search(r"loc_merged_(.+?)_outputs\.jsonl$", p.name)
                if not m:
                    return (0, p.name)
                token = m.group(1)
                nums = tuple(int(x) for x in re.findall(r"\d+", token))
                # Put the filename at the end for stable ordering
                return (*nums, p.name)

            if merged_files:
                best = sorted(merged_files, key=_key)[-1]
                paths.append(best)
            else:
                # if no merged files, leave empty; stage fallbacks added below
                pass

        # Fallback: root iid.jsonl (sometimes contains found_files)
        paths.append(args.agentless_root / f"{iid}.jsonl")

        # Optional stage fallbacks (if merged missing)
        paths.append(inst_dir / "edit_location_samples" / "loc_outputs.jsonl")
        paths.append(inst_dir / "file_level" / "loc_outputs.jsonl")
        paths.append(inst_dir / "related" / "loc_outputs.jsonl")

        file_to_lines, suspect_files = parse_agentless_locations(paths)
        line_level_localization = build_line_level_localization(file_to_lines, suspect_files)

        # --- source repo root ---
        instance_src_dir = args.source_root / iid
        repo_root = resolve_repo_root(instance_src_dir)

        localized_code = build_localized_code(
            repo_root=repo_root,
            line_level_localization=line_level_localization,
            tail_after_max=args.tail_after_max,
            fallback_head=args.fallback_head,
        )

        verified_row = verified_idx.get(iid, {})
        out_row = compose_row(schema_keys, verified_row, iid, line_level_localization, localized_code)
        out_rows.append(out_row)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    with args.out_json.open("w", encoding="utf-8") as f:
        json.dump(out_rows, f, ensure_ascii=False, indent=2)

    if args.out_jsonl:
        with args.out_jsonl.open("w", encoding="utf-8") as f:
            for r in out_rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
