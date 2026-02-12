#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This is a backup copy of run_refactor_parallel working version.

import os
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
from config_refactor import (
    # keep same as config.py
    DATASET_PATH,
    DATASET,
    ASSERTFLIP_DIR,
    RESULTS_DIR,
    max_attempts,
    model,
    phase_mode,
    max_generation_retries,
    # refactor extras
    IDS_PATH,
    PATCH_DIR,
    REFACTOR_RESULTS_DIR,
    REFACTOR_LOG_DIR,
)

load_dotenv()

NUM_WORKERS_DEFAULT = 1

# exactly same mapping as run_parallel.py
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


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_text(path: Path, text: str) -> None:
    _ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8", errors="replace")


def _docker_image_name_from_instance_id(instance_id: str) -> str:
    """MUST match run_parallel.py exactly."""
    id_docker_compatible = instance_id.replace("__", "_1776_")
    return f"swebench/sweb.eval.x86_64.{id_docker_compatible}"


def _pick_patch(patch_dir: Path, instance_id: str) -> Optional[Path]:
    """Find patch file for an instance."""
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


def get_test_dir(repo_name: str, instance_id: str) -> str:
    """Match run_parallel.py behavior."""
    if instance_id in ["psf__requests-1142", "psf__requests-1921", "psf__requests-2931"]:
        return "."
    if repo_name == "sympy":
        # same as run_parallel: infer from SWE-bench Verified test_patch
        try:
            from datasets import load_dataset
            import pandas as pd
            from unidiff import PatchSet

            ds = load_dataset(DATASET, split="test")
            dataset = pd.DataFrame(ds)
            _test_patch = dataset[dataset["instance_id"] == instance_id]["test_patch"].values[0]
            patch_set = PatchSet(_test_patch)
            for patched_file in patch_set:
                if patched_file.is_added_file:
                    continue
                file_path = patched_file.path
                if not file_path.startswith('/'):
                    file_path = '/' + file_path
                if file_path.endswith(".py"):
                    return str(Path(file_path).parent).strip("/")
        except Exception:
            pass
    return repo_directories[repo_name]["tests_dir"]


def _run_shell(cmd: str, *, timeout: Optional[int] = None, capture: bool = True) -> subprocess.CompletedProcess:
    """
    Run a shell command in a way that lets us dump stdout/stderr on failure.
    Behavior is still 'check=True' like run_parallel; we only add log capture.
    """
    return subprocess.run(
        cmd,
        shell=True,
        check=True,
        timeout=timeout,
        capture_output=capture,
        text=True,
    )


def process_instance(
    instance: Dict[str, Any],
    patch_dir: Path,
    results_dir: Path,
    log_dir: Path,
    timeout_s: int,
) -> Dict[str, Any]:
    """
    Align container lifecycle & assertflip invocation with run_parallel.py.
    Extra step: apply refactor patch before running assertflip.
    """
    instance_id = instance.get("instance_id", "")
    outcome = {"instance_id": instance_id, "status": "success", "error": ""}

    if not instance_id:
        outcome["status"] = "skipped"
        outcome["error"] = "Missing instance_id"
        return outcome

    repo_full_name = instance.get("repo", "")
    if not repo_full_name or "/" not in repo_full_name:
        outcome["status"] = "skipped"
        outcome["error"] = f"Missing/invalid repo for {instance_id}"
        return outcome

    repo_name = repo_full_name.split("/")[-1]
    if repo_name not in repo_directories:
        outcome["status"] = "skipped"
        outcome["error"] = f"Unknown repo: {repo_name}"
        return outcome

    version = str(instance.get("version", ""))
    if not version:
        outcome["status"] = "skipped"
        outcome["error"] = f"Missing version for {instance_id}"
        return outcome

    if repo_full_name not in MAP_REPO_VERSION_TO_SPECS:
        outcome["status"] = "skipped"
        outcome["error"] = f"repo {repo_full_name} not in MAP_REPO_VERSION_TO_SPECS"
        return outcome

    if version not in MAP_REPO_VERSION_TO_SPECS[repo_full_name]:
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

    # IMPORTANT: image name must match run_parallel exactly (no extra repo_name, no :latest)
    image_name = _docker_image_name_from_instance_id(instance_id)

    source_dir = repo_directories[repo_name]["source_dir"]
    tests_dir = get_test_dir(repo_name, instance_id)

    patch_path = _pick_patch(patch_dir, instance_id)

    # ensure results/log dirs exist on host
    _ensure_dir(results_dir)
    _ensure_dir(log_dir)

    # per-instance files on host
    temp_json_path = results_dir / f"{instance_id}.json"
    log_path = log_dir / f"log_{instance_id}.txt"

    container = None
    docker_client = None

    try:
        # write per-instance dataset record (same pattern as run_parallel)
        with temp_json_path.open("w", encoding="utf-8") as f:
            json.dump(instance, f, indent=2)

        # pull/cache check (same pattern as run_parallel)
        img_q = subprocess.run(["docker", "images", "-q", image_name], capture_output=True, text=True)
        if img_q.stdout.strip():
            print("Using image from cache for:", image_name)
        else:
            print("Pulling:", image_name)
            subprocess.run(["docker", "pull", image_name], check=True)

        docker_client = docker.from_env()

        env = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "AZURE_API_KEY": os.getenv("AZURE_API_KEY", ""),
            "AZURE_API_BASE": os.getenv("AZURE_API_BASE", ""),
            "AZURE_API_VERSION": os.getenv("AZURE_API_VERSION", ""),
            "CUSTOM_INSTRUCTIONS": CUSTOM_INSTRUCTIONS.get(repo_name, None),
            "PROJECT_NAME": repo_name,
        }

        # MUST align with run_parallel: mount RESULTS_DIR to /results (rw), no explicit container name
        results_dir_abs = str(results_dir.resolve())
        container = docker_client.containers.run(
            image_name,
            command="sleep infinity",
            detach=True,
            remove=False,
            volumes={
                str(results_dir_abs): {"bind": "/results", "mode": "rw"},
            },
            environment=env,
        )
        container_id = container.id

        # copy assertflip into /assertflip (same as run_parallel)
        subprocess.run(
            ["docker", "cp", ASSERTFLIP_DIR, f"{container_id}:/assertflip"],
            check=True,
        )

        # prep deps (same as run_parallel)
        prep_cmd = (
            "source /opt/miniconda3/etc/profile.d/conda.sh && "
            "conda activate testbed && "
            "python -m pip install coverage"
        )
        _run_shell(f'docker exec {container_id} bash -c "{prep_cmd}"', capture=True)

        # apply refactor patch (your existing logic; keep /testbed and flags)
        if patch_path is not None:
            subprocess.run(
                ["docker", "cp", str(patch_path), f"{container_id}:/tmp/refactor.patch"],
                check=True,
            )

            check_apply = (
                "cd /testbed && "
                "git apply --check --ignore-space-change --ignore-whitespace /tmp/refactor.patch"
            )
            try:
                _run_shell(f'docker exec {container_id} bash -c "{check_apply}"', capture=True)
            except subprocess.CalledProcessError as e:
                outcome["status"] = "error"
                outcome["error"] = "git apply --check failed"
                _write_text(
                    log_path,
                    f"[git apply --check FAILED]\npatch={patch_path}\n\nSTDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}\n",
                )
                return outcome

            apply_cmd = (
                "cd /testbed && "
                "git apply --ignore-space-change --ignore-whitespace /tmp/refactor.patch"
            )
            try:
                _run_shell(f'docker exec {container_id} bash -c "{apply_cmd}"', capture=True)
            except subprocess.CalledProcessError as e:
                outcome["status"] = "error"
                outcome["error"] = "git apply failed"
                _write_text(
                    log_path,
                    f"[git apply FAILED]\npatch={patch_path}\n\nSTDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}\n",
                )
                return outcome
        else:
            # no patch is allowed; just record to log
            _write_text(log_path, f"[WARN] No patch found for {instance_id} under {patch_dir}\n")

        # build assertflip command EXACTLY like run_parallel
        env_export = "export PYTHONWARNINGS=ignore::UserWarning,ignore::SyntaxWarning && " if repo_name == "sympy" else ""
        if repo_name == "sympy":
            test_cmd = "/testbed/bin/test -C --verbose"
        quoted_test_cmd = shlex.quote(test_cmd)

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

        try:
            _run_shell(f'docker exec {container_id} bash -c "{bash_cmd}"', timeout=timeout_s, capture=True)
        except subprocess.CalledProcessError as e:
            outcome["status"] = "error"
            outcome["error"] = "assertflip failed"
            _write_text(
                log_path,
                f"[assertflip FAILED]\nCMD:\n{bash_cmd}\n\nSTDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}\n",
            )
            return outcome

        # copy generated test back (same as run_parallel)
        generated_test_path = f"/testbed/{tests_dir}/test_assertflip_{instance_id}.py"
        local_test_path = results_dir / f"test_assertflip_{instance_id}.py"
        if file_exists_in_container(container_id, generated_test_path):
            subprocess.run(
                ["docker", "cp", f"{container_id}:{generated_test_path}", str(local_test_path)],
                check=True,
            )

        return outcome

    except Exception as e:
        outcome["status"] = "error"
        outcome["error"] = str(e)
        _write_text(log_path, f"[UNCAUGHT ERROR]\n{e}\n")
        return outcome

    finally:
        # same teardown pattern as run_parallel
        try:
            if container is not None:
                container.stop()
                container.remove()
        except docker.errors.APIError:
            pass
        try:
            temp_json_path.unlink(missing_ok=True)
        except Exception:
            pass


def parse_args(argv=None):
    import argparse
    ap = argparse.ArgumentParser(
        prog="run_refactor_parallel.py",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    ap.add_argument("--ids", default=IDS_PATH, type=str, help="Path to ids.json")
    ap.add_argument("--dataset", default=DATASET_PATH, type=str, help="Dataset json path")
    ap.add_argument("--patch-dir", default=PATCH_DIR, type=str, help="Directory containing refactor patches")
    ap.add_argument("--out-dir", default=REFACTOR_RESULTS_DIR, type=str, help="Host output directory mounted to /results")
    ap.add_argument("--log-dir", default=REFACTOR_LOG_DIR, type=str, help="Extra logs output dir")
    ap.add_argument("--max-workers", default=NUM_WORKERS_DEFAULT, type=int, help="Parallel workers")
    ap.add_argument("--timeout", default=3600, type=int, help="Per-instance docker exec timeout (seconds)")
    ap.add_argument("--seed", default=0, type=int, help="Seed (reserved)")
    ap.add_argument("--strategy", default="all", type=str, help="Reserved (CLI compatibility)")
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    ids_path = Path(args.ids).resolve()
    dataset_path = Path(args.dataset).resolve()
    patch_dir = Path(args.patch_dir).resolve()
    results_dir = Path(args.out_dir).resolve()
    log_dir = Path(args.log_dir).resolve()

    _ensure_dir(results_dir)
    _ensure_dir(log_dir)

    ids_obj = _read_json(ids_path)
    if not isinstance(ids_obj, list):
        raise ValueError("--ids must be a JSON list")

    instance_ids: List[str] = []
    for it in ids_obj:
        if isinstance(it, str):
            instance_ids.append(it)
        elif isinstance(it, dict) and "instance_id" in it:
            instance_ids.append(str(it["instance_id"]))
        else:
            raise ValueError("ids.json must be list[str] or list[{'instance_id': ...}]")

    dataset_obj = _read_json(dataset_path)
    dataset_index: Dict[str, Dict[str, Any]] = {}

    if isinstance(dataset_obj, dict):
        for k, v in dataset_obj.items():
            if isinstance(v, dict):
                dataset_index[str(k)] = v
    elif isinstance(dataset_obj, list):
        for rec in dataset_obj:
            if isinstance(rec, dict) and "instance_id" in rec:
                dataset_index[str(rec["instance_id"])] = rec
    else:
        raise ValueError("dataset json must be list[dict] or dict[str, dict]")

    instances: List[Dict[str, Any]] = []
    for iid in instance_ids:
        rec = dataset_index.get(iid)
        if rec is None:
            # keep a minimal record so we can report a clean skip/error
            instances.append({"instance_id": iid})
        else:
            instances.append(rec)

    error_counter = 0
    skipped_counter = 0

    with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(process_instance, inst, patch_dir, results_dir, log_dir, args.timeout): inst.get("instance_id", "<unknown>")
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

    print(f"Finished. Errors: {error_counter}, Skipped: {skipped_counter}")
    print(f"Out dir: {results_dir}")
    print(f"Log dir: {log_dir}")


if __name__ == "__main__":
    main()
