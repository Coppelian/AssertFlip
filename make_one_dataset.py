# make_one_dataset.py
import json, sys
from datasets import load_dataset

DATASET = "princeton-nlp/SWE-bench_Verified"

def to_assertflip_record(rec):
    return {
        "instance_id": rec["instance_id"],
        "problem_statement": rec["problem_statement"],
        # 部分来源只有 patch，没有 localized_code；做个兜底
        "localized_code": rec.get("localized_code", rec.get("patch", "")),
        "line_level_localization": rec.get("line_level_localization", []),
    }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python make_one_dataset.py <instance_id> <out_path>")
        sys.exit(1)

    iid, out_path = sys.argv[1], sys.argv[2]

    # 拉取 test split（SWE-bench Verified 的官方分割）
    ds = load_dataset(DATASET, split="test")  # 需要联网首拉；本地缓存后离线可用
    # 过滤出目标 id（也可用 .filter，更快更地道）
    row = next((r for r in ds if r["instance_id"] == iid), None)
    if row is None:
        raise SystemExit(f"instance_id not found in test split: {iid}")

    out = to_assertflip_record(row)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("Wrote", out_path)

