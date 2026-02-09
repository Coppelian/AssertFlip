import json
from pathlib import Path
from datasets import load_dataset

# Paths
PIPE = Path(__file__).resolve().parent
IDS_PATH = PIPE / "ids.json"
OUT_PATH = PIPE / "dataset_in.json"

# Choose dataset source (most common baseline for these instance_ids)
DATASET_NAME = "princeton-nlp/SWE-bench_Verified"
SPLIT = "test"

def main():
    ids = set(json.loads(IDS_PATH.read_text(encoding="utf-8")))
    print(f"Target ids: {len(ids)}")

    print(f"Loading dataset: {DATASET_NAME} [{SPLIT}] ...")
    ds = load_dataset(DATASET_NAME, split=SPLIT)

    found = []
    found_ids = set()

    # Streaming scan (dataset isn't huge, but this is simplest)
    for rec in ds:
        iid = rec.get("instance_id")
        if iid in ids:
            found.append(rec)
            found_ids.add(iid)

    missing = sorted(ids - found_ids)
    print(f"Found: {len(found)} / {len(ids)}")
    if missing:
        print("Missing ids:")
        for m in missing:
            print("  ", m)

    OUT_PATH.write_text(json.dumps(found, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote:", OUT_PATH)

if __name__ == "__main__":
    main()
