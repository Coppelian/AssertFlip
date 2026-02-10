import json
from pathlib import Path
from datasets import load_dataset

# ========= 路径配置 =========
DATASET_OUT = Path("dataset_out.json")
OUTPUT_DATASET = Path("dataset_out_with_image.json")

# 本地缓存 SWE-bench
SWE_BENCH_JSON = Path("SWE-bench_Verified.json")

SWE_BENCH_NAME = "SWE-bench/SWE-bench_Verified"
# SWE_BENCH_SPLIT = "verified"
# ============================

def main():
    print("[INFO] Loading SWE-bench_Verified from HuggingFace datasets...")
    swebench = load_dataset(
        SWE_BENCH_NAME,
        # SWE_BENCH_SPLIT,
        split="test"
    )

    # 1. 保存完整 SWE-bench_Verified.json（只做一次即可）
    if not SWE_BENCH_JSON.exists():
        print(f"[INFO] Saving full SWE-bench_Verified to {SWE_BENCH_JSON}")
        with SWE_BENCH_JSON.open("w") as f:
            json.dump(list(swebench), f, indent=2)
    else:
        print(f"[INFO] {SWE_BENCH_JSON} already exists, skip saving")

    # 2. 构建 instance_id -> image 映射
    id2image = {}
    for inst in swebench:
        iid = inst.get("instance_id")
        img = inst.get("image")
        if iid and img:
            id2image[iid] = img

    print(f"[INFO] Collected image for {len(id2image)} instances")

    # 3. 加载你的 dataset_out.json
    with DATASET_OUT.open() as f:
        out_data = json.load(f)

    injected = 0
    missing = []

    for inst in out_data:
        iid = inst.get("instance_id")
        if not iid:
            continue

        if not inst.get("image"):
            if iid in id2image:
                inst["image"] = id2image[iid]
                injected += 1
            else:
                missing.append(iid)

    # 4. 输出新 dataset_out
    with OUTPUT_DATASET.open("w") as f:
        json.dump(out_data, f, indent=2)

    print(f"[DONE] Injected image for {injected} instances")
    if missing:
        print(f"[WARN] {len(missing)} instances missing in SWE-bench_Verified:")
        for iid in missing:
            print("  -", iid)

if __name__ == "__main__":
    main()
