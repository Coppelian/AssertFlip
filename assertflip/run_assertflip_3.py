# file: run_assertflip_3.py
import json, os, subprocess, sys, pathlib, shlex

# 1) 保证能找到包：建议也可用 pip install -e assertflip/
PKG_ROOT = pathlib.Path(__file__).resolve().parent
ENV = dict(os.environ)
ENV["PYTHONPATH"] = f"{PKG_ROOT/'assertflip'/'src'}:{ENV.get('PYTHONPATH','')}"

# 2) 读取需要跑的实例 ID 列表（逗号分隔）
INSTANCE_IDS = ["django__django-11333","sympy__sympy-20590","pytest-dev__pytest-11171"]
OUT_PATH = "assertflip.swebench.jsonl"

# 3) 约定每个实例有单独的 dataset 文件：datasets/{instance_id}.json
DATASET_DIR = PKG_ROOT / "datasets"
TESTS_DIR   = PKG_ROOT / "tests"

def run_one_instance(iid: str) -> str:
    dataset_path = DATASET_DIR / f"{iid}.json"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    # 清理 tests 目录的工作区改动，保证 diff 干净
    subprocess.run(["git","checkout","--","tests"], check=False)

    # 4) 调用包入口：相当于 python -m assertFlip --dataset <file> ...
    cmd = [
        sys.executable, "-m", "assertFlip",
        "--dataset", str(dataset_path),
        "--tests-dir", str(TESTS_DIR),
        "--prompt", "gpt-v2",
        "--phase", "both",
        "--model", os.environ.get("ASSERTFLIP_MODEL","gpt-4o"),
        "--max-generation-retries", "10",
    ]
    print("RUN:", " ".join(shlex.quote(c) for c in cmd))
    subprocess.run(cmd, check=True, env=ENV)

    # 5) 只导出 tests/** 的 patch
    patch = subprocess.check_output(["git","diff","--unified=0","--","tests"], env=ENV).decode("utf-8", "ignore")
    return patch

def main():
    with open(OUT_PATH, "w", encoding="utf-8") as fw:
        for iid in INSTANCE_IDS:
            patch = run_one_instance(iid)
            rec = {
                "instance_id": iid,
                "model_name_or_path": os.environ.get("ASSERTFLIP_MODEL","AssertFlip-Local"),
                "model_patch": patch
            }
            fw.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()

