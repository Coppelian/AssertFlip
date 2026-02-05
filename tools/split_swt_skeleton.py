#!/usr/bin/env python3
import json, argparse
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skeleton", required=True, help="Path to SWT_Verified_Test_Source_Skeleton.json")
    ap.add_argument("--out", default="datasets", help="Output directory for per-instance JSON files")
    ap.add_argument("--limit", type=int, default=0, help="Optionally limit how many to extract (0 = all)")
    args = ap.parse_args()

    src = Path(args.skeleton)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(src.read_text(encoding="utf-8"))
    # The file is a list of dicts where each dict has 'instance_id', 'problem_statement',
    # 'localized_code', 'line_level_localization', etc.
    if isinstance(data, dict):
        # try common container key
        for k in ("instances","data","items","records"):
            if k in data and isinstance(data[k], list):
                data = data[k]
                break

    count = 0
    for item in data:
        if not isinstance(item, dict) or "instance_id" not in item:
            continue
        iid = item["instance_id"]
        minimal = {
            "instance_id": iid,
            "problem_statement": item.get("problem_statement",""),
            "localized_code": item.get("localized_code",""),
            "line_level_localization": item.get("line_level_localization", []),
        }
        (out_dir / f"{iid}.json").write_text(json.dumps(minimal, ensure_ascii=False, indent=2), encoding="utf-8")
        count += 1
        if args.limit and count >= args.limit:
            break

    print(f"Wrote {count} instance files to {out_dir}")

if __name__ == "__main__":
    main()

