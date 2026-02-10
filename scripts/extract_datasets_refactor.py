#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extract a refactor-only dataset (9 cases) from a large dataset_out.json.

Inputs:
  --ids       path to ids.json (a list: ["id1","id2",...])
  --dataset   path to dataset_out.json (a list of instance dicts)
Optional:
  --agentless_dir   directory containing <instance_id>.jsonl, used only for sanity check
Outputs:
  --out_dir   output directory, will write:
              - dataset_9.json
              - per_instance/<instance_id>.json
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Any


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True, help="path to ids.json (list of instance_id)")
    ap.add_argument("--dataset", required=True, help="path to dataset_out.json (large metadata json)")
    ap.add_argument("--out_dir", required=True, help="output directory")
    ap.add_argument(
        "--agentless_dir",
        default=None,
        help="optional: directory containing <instance_id>.jsonl to sanity-check existence",
    )
    args = ap.parse_args()

    ids_path = Path(args.ids)
    dataset_path = Path(args.dataset)
    out_dir = Path(args.out_dir)

    ids: List[str] = load_json(ids_path)
    if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids):
        raise ValueError("ids.json must be a JSON list of strings")

    dataset = load_json(dataset_path)
    if not isinstance(dataset, list):
        raise ValueError("dataset_out.json must be a JSON list (array)")

    # index by instance_id
    by_id: Dict[str, Dict[str, Any]] = {}
    for inst in dataset:
        iid = inst.get("instance_id")
        if isinstance(iid, str):
            by_id[iid] = inst

    missing = [iid for iid in ids if iid not in by_id]

    # optional sanity check for agentless jsonl existence
    missing_jsonl = []
    if args.agentless_dir:
        adir = Path(args.agentless_dir)
        for iid in ids:
            if not (adir / f"{iid}.jsonl").exists():
                missing_jsonl.append(iid)

    selected: List[Dict[str, Any]] = []
    for iid in ids:
        if iid in by_id:
            selected.append(by_id[iid])

    # Write outputs
    out_dataset_path = out_dir / "dataset_9.json"
    per_instance_dir = out_dir / "per_instance"
    dump_json(out_dataset_path, selected)

    for inst in selected:
        iid = inst["instance_id"]
        dump_json(per_instance_dir / f"{iid}.json", inst)

    # Print summary
    print("=== Extract summary ===")
    print(f"ids count: {len(ids)}")
    print(f"selected count: {len(selected)}")
    print(f"missing in dataset_out.json: {len(missing)}")
    if missing:
        print("  missing:", missing)

    if args.agentless_dir:
        print(f"missing agentless jsonl under {args.agentless_dir}: {len(missing_jsonl)}")
        if missing_jsonl:
            print("  missing_jsonl:", missing_jsonl)

    print(f"\nWrote:\n  {out_dataset_path}\n  {per_instance_dir}/<instance_id>.json")


if __name__ == "__main__":
    main()
