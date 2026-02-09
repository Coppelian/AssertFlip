#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from datasets import load_dataset

IDS_PATH = Path("ids.json")                  # 你的 ids.json
OUT_PATH = Path("SWE-bench_Verified.jsonl")  # 生成的 verified 快照

def load_ids(path: Path):
    obj = json.load(path.open())
    if isinstance(obj, list):
        return set(obj)
    if isinstance(obj, dict) and "ids" in obj:
        return set(obj["ids"])
    raise ValueError("ids.json must be list or {'ids': [...]}")

def main():
    ids = load_ids(IDS_PATH)

    print(f"[+] Loading SWE-bench Verified from HuggingFace")
    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")

    kept = 0
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for row in ds:
            iid = row.get("instance_id")
            if iid in ids:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                kept += 1

    print(f"[✓] Wrote {kept} instances to {OUT_PATH}")

if __name__ == "__main__":
    main()
