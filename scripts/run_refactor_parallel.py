#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import shlex
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

import docker
from dotenv import load_dotenv
from tqdm import tqdm

from constants import MAP_REPO_VERSION_TO_SPECS, CUSTOM_INSTRUCTIONS
from config import (
    DATASET,                 # 仍可用于 sympy 的测试目录推导
    ASSERTFLIP_DIR,          # ✅ 不再猜，直接用 config
    max_attempts,
    model,
    phase_mode,
    max_generation_retries,
)

# ✅ 按你要求：run_refactor_parallel 唯一不使用 config 的地方：DATASET_PATH 固定为 refactor dataset
DATASET_PATH = "./datasets_refactor/dataset_out.json"

# 你原来 run_parallel 用的是 RESULTS_DIR 作为默认输出目录；
# 这里仍支持 CLI 覆盖 --out-dir
DEFAULT_OUT_DIR = "./outputs_refactor"

load_dotenv()

NUM_WORKERS_DEFAULT = 1

# 与 run_parallel.py 保持一致
repo_directories = {
    'flask': {'source_dir': 'src/flask', 'tests_dir': 'tests'},
    'django': {'source_dir': 'django', 'tests_dir': 'tests'},
    'matplotlib': {'source_dir': 'lib/matplotlib', 'tests_dir': 'lib/matplotlib/tests'},
    'pylint': {'source_dir': 'pylint', 'tests_dir': 'tests'},
    'pytest': {'source_dir': 'src/_pytest', 'tests_dir': 'testing'},
    'requests': {'source_dir': 'requests', 'tests_dir': 'tests'},
    'scikit-learn': {'source_dir': 'sklearn', 'tests_dir': 'sklearn/tests'},
    'seaborn': {'source_dir': 'seaborn', 'tests_dir': 'tests'},
    'sphinx': {'source_dir': 'sphinx', 'tests_dir': 'tests'},
    'sympy': {'source_dir': 'sympy', 'tests_dir': 'sympy/testing'},
    'astropy': {'source_dir': 'astropy', 'tests_dir': 'astropy/tests'},
    'xarray': {'source_dir': 'xarray', 'tests_dir': 'xarray/tests'}
}

NON_TEST_EXTS = [
    ".json", ".png", "csv", ".txt", ".md", ".jpg", ".jpeg", ".pkl", ".yml",
    ".yaml", ".toml",
]


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _safe_sh(cmd: List[str], *, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def _docker_image_name_from_instance_id(instance_id: str) -> str:
    """✅ 与 run_parallel.py 完全一致"""
    id_docker_compatible = instance_id.replace("__", "_1776_")
    return f"swebench/sweb.eval.x86_64.{id_docker_compatible}"


def _pick_patch(patch_dir: Path, instance_id: str) -> Optional[Path]:
    """为 instance 选择 patch 文件。
    支持：
      - <patch_dir>/<instance_id>.patch
      - <patch_dir>/<instance_id>.diff
      - 任意以 instance_id 开头，后缀为 .patch/.diff
    """
    direct = [patch_dir / f"{instance_id}.patch", patch_dir / f"{instance_id}.diff"]
    for p in direct:
        if p.exists() and p.is_file():
            return p

    for ext in (".patch", ".diff"):
        cands = sorted(patch_dir.glob(f"{instance_id}*{ext}"))
        if cands:
            return cands[0]
    return None


def file_exists_in_container(container_id: str, file_path: str) -> bool:
    check_cmd = f"test -f {shlex.quote(file_path)}"
    result = subprocess.run(
        ["docker", "exec", container_id, "bash", "-c", check_cmd],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0


def get_test_dir(repo_name: str, instance: Dict[str, Any]) -> str:
    """尽量与 run_parallel.py 保持一致。
    如果 refactor dataset 中缺少某些字段，这里会更保守地回退到默认 tests_dir。
    """
    instance_id = instance["instance_id"]

    # run_parallel 的特殊 case
    if instance_id in ["psf__requests-1142", "psf__requests-1921", "psf__requests-2931"]:
        return "."

    # sympy：run_parallel 会从 SWE-bench_Verified 里解析 test_patch 找实际目录
    if repo_name == "sympy":
        try:
            from datasets import load_dataset
            import pandas as pd
            from unidiff import PatchSet

            ds = load_dataset(DATASET, split="test")
            dataset = pd.DataFrame(ds)
            _test_patch = dataset[dataset["instance_id"] == instance_id]["test_patch"].values[0]

            try:
                patch_set = PatchSet(_test_patch)
            except Exception:
                patch_set = None

            if patch_set:
                for patched_file in patch_set:
                    if patched_file.is_added_file:
                        continue
                    file_path = patched_file.path
                    if not file_path.startswith('/'):
                        file_path = '/' + file_path
                    if file_path.endswith(".py"):
                        return str(Path(file_path).parent).strip("/")
        except Exception:
            # refactor 数据不全或 datasets 不可用时，回退默认
            pass

    return repo_directories[repo_name]['tests_dir']


def process_instance(
    instance: Dict[str, Any],
    patch_dir: Path,
    out_dir: Path,
    timeout_s: int,
) -> Dict[str, Any]:
    """对齐 run_parallel：每个实例独立 docker container 跑 AssertFlip。
    额外：先 git apply refactor patch。
    """
    instance_id = instance["instance_id"]
    outcome = {"instance_id": instance_id, "status": "success", "error": ""}

    repo_full_name = instance.get("repo", "")
    if not repo_full_name or "/" not in repo_full_name:
        outcome["status"] = "skipped"
        outcome["error"] = f"Missing/invalid repo field in dataset_out for {instance_id}"
        return outcome

    repo_name = repo_full_name.split("/")[-1]
    if repo_name not in repo_directories:
        outcome["status"] = "skipped"
        outcome["error"] = f"Unknown repo: {repo_name}"
        return outcome

    image_name = _docker_image_name_from_instance_id(instance_id)

    # 这里仍使用 MAP_REPO_VERSION_TO_SPECS 来得到 test_cmd / eval_commands（对齐 run_parallel）
    version = str(instance.get("version", ""))
    if not version:
        outcome["status"] = "skipped"
        outcome["error"] = f"Missing version field in dataset_out for {instance_id}"
        return outcome

    if repo_full_name not in MAP_REPO_VERSION_TO_SPECS:
        outcome["status"] = "skipped"
        outcome["error"] = f"repo {repo_full_name} not in MAP_REPO_VERSION_TO_SPECS"
        return outcome

    if version not in MAP_REPO_VERSION_TO_SPECS[repo_full_name]:
        # run_parallel 的 0 补位逻辑
        version_alt = version + "0"
        if version_alt not in MAP_REPO_VERSION_TO_SPECS[repo_full_name]:
            outcome["status"] = "skipped"
            outcome["error"] = f"Version {version} not in specs"
            return outcome
        version = version_alt

    spec = MAP_REPO_VERSION_TO_SPECS[repo_full_name][version]
    test_cmd = spec["test_cmd"]
    eval_commands = spec.get("eval_commands", [])

    if isinstance(test_cmd, list):
        test_cmd = test_cmd[-1]

    source_dir = repo_directories[repo_name]["source_dir"]
    tests_dir = get_test_dir(repo_name, instance)

    # patch：允许没有（不炸），但会记录
    patch_path = _pick_patch(patch_dir, instance_id)

    # out dir mount 对齐 run_parallel：挂载到 /results
    out_dir_abs = str(out_dir.resolve())
    _ensure_dir(out_dir)

    try:
        # pull / cache
        result = subprocess.run(["docker", "images", "-q", image_name], capture_output=True, text=True)
        image_stored = bool(result.stdout.strip())
        if image_stored:
            print("Using image from cache for:", image_name)
        else:
            print("Pulling:", image_name)
            subprocess.run(["docker", "pull", image_name], check=True)

        docker_client = docker.from_env()

        env = {
            # 允许 openai/azure 都传（不影响），由 model 决定用哪个
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "AZURE_API_KEY": os.getenv("AZURE_API_KEY", ""),
            "AZURE_API_BASE": os.getenv("AZURE_API_BASE", ""),
            "AZURE_API_VERSION": os.getenv("AZURE_API_VERSION", ""),
            "CUSTOM_INSTRUCTIONS": CUSTOM_INSTRUCTIONS.get(repo_name, None),
            "PROJECT_NAME": repo_name,
        }

        container = docker_client.containers.run(
            image_name,
            command="sleep infinity",
            detach=True,
            remove=False,
            volumes={out_dir_abs: {"bind": "/results", "mode": "rw"}},
            environment=env,
        )
        container_id = container.id

        # 1) 把 assertflip 复制进容器（对齐 run_parallel）
        container_assertflip_path = "/assertflip"
        subprocess.run(
            ["docker", "cp", ASSERTFLIP_DIR, f"{container_id}:{container_assertflip_path}"],
            check=True,
        )

        # 2) 基础准备（对齐 run_parallel）
        env_export = "export PYTHONWARNINGS=ignore::UserWarning,ignore::SyntaxWarning && " if repo_name == "sympy" else ""
        if repo_name == "sympy":
            test_cmd = "/testbed/bin/test -C --verbose"
        quoted_test_cmd = shlex.quote(test_cmd)

        prep_cmd = (
            "source /opt/miniconda3/etc/profile.d/conda.sh && "
            "conda activate testbed && "
            "python -m pip install coverage"
        )
        subprocess.run(f'docker exec {container_id} bash -c "{prep_cmd}"', shell=True, check=True)

        # 3) patch apply（安全化：先 --check，再 apply）
        if patch_path is not None:
            # copy patch
            subprocess.run(
                ["docker", "cp", str(patch_path), f"{container_id}:/tmp/refactor.patch"],
                check=True,
            )
            # check
            check_apply = (
                "cd /testbed && "
                "git apply --check --ignore-space-change --ignore-whitespace /tmp/refactor.patch"
            )
            check_p = subprocess.run(
                f'docker exec {container_id} bash -c "{check_apply}"',
                shell=True, capture_output=True, text=True
            )
            if check_p.returncode != 0:
                outcome["status"] = "error"
                outcome["error"] = (
                    "git apply --check failed\n"
                    f"patch={patch_path.name}\n"
                    f"stdout:\n{check_p.stdout}\n"
                    f"stderr:\n{check_p.stderr}\n"
                )
                return outcome

            # apply
            apply_cmd = (
                "cd /testbed && "
                "git apply --ignore-space-change --ignore-whitespace /tmp/refactor.patch"
            )
            subprocess.run(f'docker exec {container_id} bash -c "{apply_cmd}"', shell=True, check=True)
        else:
            # 不炸：只记录
            print(f"[WARN] No patch found for {instance_id} under {patch_dir}")

        # 4) 把该 instance 的 dataset record 写到 /results/<id>.json （对齐 run_parallel 的 per-instance json）
        temp_json_path = out_dir / f"{instance_id}.json"
        with temp_json_path.open("w", encoding="utf-8") as f:
            json.dump(instance, f, indent=2)

        # 5) 运行 assertflip（对齐 run_parallel 的 bash_cmd 结构）
        eval_cmd_str = " && ".join(eval_commands) + " && " if eval_commands else ""

        bash_cmd = (
            f"{env_export}{eval_cmd_str}"
            "pip install /assertflip && "
            "pip install hypothesis && "
            f"assertflip --test-cmd {quoted_test_cmd} "
            f"--source-dir {source_dir} "
            f"--tests-dir {tests_dir} "
            f"--max-attempts {max_attempts} "
            f"--dataset /results/{instance_id}.json "
            f"--model {model} "
            f"--phase {phase_mode} "
            f"--max-generation-retries {max_generation_retries} "
            f"--max-attempts {max_attempts} "
        )

        subprocess.run(
            f'docker exec {container_id} bash -c "{bash_cmd}"',
            shell=True,
            check=True,
            timeout=timeout_s,
        )

        # 6) 拷贝生成测试文件（对齐 run_parallel）
        generated_test_path = f"/testbed/{tests_dir}/test_assertflip_{instance_id}.py"
        local_test_path = out_dir / f"test_assertflip_{instance_id}.py"
        if file_exists_in_container(container_id, generated_test_path):
            subprocess.run(
                ["docker", "cp", f"{container_id}:{generated_test_path}", str(local_test_path)],
                check=True,
            )

        return outcome

    except Exception as e:
        outcome["status"] = "error"
        outcome["error"] = str(e)
        return outcome

    finally:
        # teardown（对齐 run_parallel）
        try:
            if "container" in locals():
                container.stop()
                container.remove()
        except docker.errors.APIError:
            pass


def parse_args(argv=None):
    import argparse
    ap = argparse.ArgumentParser(
        prog="run_refactor_parallel.py",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    ap.add_argument("--ids", required=True, type=str, help="Path to ids.json (list of instance_id)")
    ap.add_argument("--dataset", default=None, type=str, help="Optional override dataset path (default uses DATASET_PATH constant)")
    ap.add_argument("--patch-dir", required=True, type=str, help="Directory containing refactor patches")
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR, type=str, help="Output directory mounted to /results")
    ap.add_argument("--max-workers", default=NUM_WORKERS_DEFAULT, type=int, help="Parallel workers")
    ap.add_argument("--timeout", default=3600, type=int, help="Per-instance docker exec timeout (seconds)")
    ap.add_argument("--seed", default=0, type=int, help="Seed (reserved, consistent with your CLI)")
    ap.add_argument("--strategy", default="all", type=str, help="Reserved (kept for CLI compatibility)")
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    ids_path = Path(args.ids).resolve()
    patch_dir = Path(args.patch_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    _ensure_dir(out_dir)

    dataset_path = Path(args.dataset).resolve() if args.dataset else Path(DATASET_PATH).resolve()
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    ids_obj = _read_json(ids_path)
    if not isinstance(ids_obj, list):
        raise ValueError("--ids must be a JSON list")
    instance_ids = []
    for it in ids_obj:
        if isinstance(it, str):
            instance_ids.append(it)
        elif isinstance(it, dict) and "instance_id" in it:
            instance_ids.append(str(it["instance_id"]))
        else:
            raise ValueError("ids.json must be list[str] or list[{'instance_id': ...}]")

    dataset_obj = _read_json(dataset_path)
    if isinstance(dataset_obj, dict):
        # dict keyed by instance_id
        dataset_index: Dict[str, Dict[str, Any]] = {
            str(k): v for k, v in dataset_obj.items() if isinstance(v, dict)
        }
    elif isinstance(dataset_obj, list):
        dataset_index = {}
        for rec in dataset_obj:
            if isinstance(rec, dict) and "instance_id" in rec:
                dataset_index[str(rec["instance_id"])] = rec
    else:
        raise ValueError("dataset_out.json must be list[dict] or dict[str, dict]")

    # 只跑 ids 里指定的（对齐你的用法）
    instances: List[Dict[str, Any]] = []
    for iid in instance_ids:
        rec = dataset_index.get(iid)
        if not rec:
            # 保守：没有 record 就跳过
            instances.append({"instance_id": iid})
        else:
            instances.append(rec)

    error_counter = 0
    skipped_counter = 0

    with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(process_instance, inst, patch_dir, out_dir, args.timeout): inst.get("instance_id", "<unknown>")
            for inst in instances
        }
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Processing"):
            iid = futures[fut]
            try:
                result = fut.result()
            except Exception as e:
                error_counter += 1
                print(f"[ERROR] {iid}: {e}")
                continue

            if result["status"] == "error":
                error_counter += 1
                print(f"[ERROR] {result['instance_id']}: {result['error']}")
            elif result["status"] == "skipped":
                skipped_counter += 1

    print(f"Finished. Errors: {error_counter}, Skipped: {skipped_counter}, Out: {out_dir}")


if __name__ == "__main__":
    main()
