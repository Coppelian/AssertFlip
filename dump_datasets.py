import json
from datasets import load_dataset

TARGET_IDS = {
    "astropy__astropy-7606",
    "astropy__astropy-8707",
    "astropy__astropy-8872",
    "astropy__astropy-12907",
    "astropy__astropy-13977",
    "django__django-10097",
    "matplotlib__matplotlib-20488",
    "matplotlib__matplotlib-25479",
    "scikit-learn__scikit-learn-26194",
}

# 你可以按需切换下面这个 dataset
# 常见可选：
#   "princeton-nlp/SWE-bench_Verified"
#   "SWT-Bench/SWT-Bench_Verified"
DATASET_NAME = "princeton-nlp/SWE-bench_Verified"
SPLIT = "test"

print(f"Loading dataset: {DATASET_NAME} [{SPLIT}]")
ds = load_dataset(DATASET_NAME, split=SPLIT)

found = {}
for rec in ds:
    iid = rec.get("instance_id")
    if iid in TARGET_IDS:
        found[iid] = rec

print(f"Found {len(found)} / {len(TARGET_IDS)} instances")

missing = TARGET_IDS - set(found.keys())
if missing:
    print("Missing:")
    for m in sorted(missing):
        print("  ", m)

# 每个 instance 单独 dump，方便你检查
for iid, rec in found.items():
    out_path = f"{iid}.raw.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2, ensure_ascii=False)
    print("Wrote:", out_path)

# 额外：只抽取 localization 相关字段，方便你对比
summary = {}
for iid, rec in found.items():
    summary[iid] = {
        "has_line_level_localization": "line_level_localization" in rec,
        "line_level_localization": rec.get("line_level_localization"),
        "has_suspect_lines": any(
            "suspect_lines" in loc
            for loc in rec.get("line_level_localization", [])
        ) if rec.get("line_level_localization") else False,
    }

with open("localization_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print("Wrote: localization_summary.json")
