import json
import os
import shlex
from pathlib import Path
import docker

ROOT = Path(__file__).resolve().parent.parent  # AssertFlip/
PIPE = ROOT / "agentless_pipeline"
OUT_DIR = PIPE / "out"
RAW_DIR = OUT_DIR / "raw_agentless"
RAW_DIR.mkdir(parents=True, exist_ok=True)

IDS_PATH = PIPE / "ids.json"
PATCH_DIR = ROOT / "patch"
AGENTLESS_DIR = ROOT / "third_party" / "Agentless"

# Agentless runtime env inside SWE-bench container
AGENTLESS_ENV = "agentless_py311"

# Dataset choice
DEFAULT_DATASET = "princeton-nlp/SWE-bench_Verified"
FALLBACK_DATASET = "princeton-nlp/SWE-bench_Lite"  # optional (we can try Lite first if you want)
USE_FALLBACK = False  # set True if you want Lite->Verified auto switching

# Hyperparams
TOP_N = 3
NUM_SAMPLES = 4
TEMPERATURE = 0.8
NUM_THREADS = 4

FAILURES_PATH = OUT_DIR / "failures.jsonl"


def swebench_image_for_instance(instance_id: str) -> str:
    docker_compatible = instance_id.replace("__", "_1776_")
    return f"swebench/sweb.eval.x86_64.{docker_compatible}"


def run_in_container(container, cmd: str) -> None:
    api = container.client.api
    exec_id = api.exec_create(
        container.id,
        cmd=["bash", "-lc", cmd],
        stdout=True,
        stderr=True,
        stdin=False,
        tty=False,
    )["Id"]

    for chunk in api.exec_start(exec_id, stream=True, demux=False):
        if isinstance(chunk, (bytes, bytearray)):
            print(chunk.decode("utf-8", errors="replace"), end="")
        else:
            print(chunk, end="")

    info = api.exec_inspect(exec_id)
    exit_code = info.get("ExitCode")
    if exit_code != 0:
        raise RuntimeError(f"Command failed (exit_code={exit_code}): {cmd}")


def docker_cp(src: Path, container_name: str, dest: str) -> None:
    cmd = f"docker cp {shlex.quote(str(src))} {shlex.quote(container_name)}:{shlex.quote(dest)}"
    rc = os.system(cmd)
    if rc != 0:
        raise RuntimeError(f"docker cp failed: {cmd}")


def append_failure(record: dict) -> None:
    FAILURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FAILURES_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    if not IDS_PATH.exists():
        raise FileNotFoundError(f"Missing ids.json: {IDS_PATH}")
    if not AGENTLESS_DIR.exists():
        raise FileNotFoundError(f"Missing Agentless repo at {AGENTLESS_DIR}")
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY is not set in your shell.")

    ids = json.loads(IDS_PATH.read_text(encoding="utf-8"))
    client = docker.from_env()

    # bind results dir into container
    results_host = OUT_DIR.resolve()
    volumes = {str(results_host): {"bind": "/results", "mode": "rw"}}

    for iid in ids:
        print("\n" + "=" * 92)
        print("INSTANCE:", iid)

        patch_path = PATCH_DIR / f"{iid}.patch"
        if not patch_path.exists():
            append_failure({"instance_id": iid, "stage": "precheck", "error": f"missing patch {patch_path}"})
            print("[SKIP] missing patch:", patch_path)
            continue

        image = swebench_image_for_instance(iid)
        print("IMAGE:", image)

        container = client.containers.run(
            image=image,
            command="bash -lc 'sleep infinity'",
            detach=True,
            tty=True,
            volumes=volumes,
            environment={
                "OPENAI_API_KEY": os.environ["OPENAI_API_KEY"],
                # optional: speed up HF downloads if set on host
                "HF_TOKEN": os.environ.get("HF_TOKEN", ""),
            },
        )

        try:
            # copy code + patches into container
            docker_cp(AGENTLESS_DIR, container.name, "/agentless")
            docker_cp(PATCH_DIR, container.name, "/refactor_patches")

            # [1/4] Apply refactor patch on /testbed
            patch_in = f"/refactor_patches/{iid}.patch"
            patch_cmd = (
                "set -e; cd /testbed; "
                "git reset --hard; git clean -fdx; "
                f"git apply{shlex.quote(patch_in)}; "
                "echo '[patch] applied'; "
                "git status --porcelain | head -n 50; "
            )
            print("\n[1/4] Apply refactor patch to /testbed")
            run_in_container(container, patch_cmd)

            # [2/4] Ensure agentless env exists & deps ready (anthropic already handled in your earlier steps)
            install_cmd = (
                "set -e; "
                "source /opt/miniconda3/etc/profile.d/conda.sh; "
                f"if ! conda env list | awk '{{print $1}}' | grep -qx {shlex.quote(AGENTLESS_ENV)}; then "
                f"  conda create -y -n {shlex.quote(AGENTLESS_ENV)} python=3.11 >/dev/null; "
                "fi; "
                f"conda activate {shlex.quote(AGENTLESS_ENV)}; "
                "python -V; "
                "python -m pip install -U pip setuptools wheel; "
                "cd /agentless; "
                "pip install -r requirements.txt; "
                "python -c \"import anthropic; import agentless; print('agentless deps ok')\"; "
            )
            print(f"\n[2/4] Install Agentless deps in container ({AGENTLESS_ENV})")
            try:
                run_in_container(container, install_cmd)
            except Exception as e:
                append_failure({"instance_id": iid, "stage": "install", "error": str(e)})
                raise

            # [3/4] Run localization pipeline with explicit dataset + artifact checks
            out_base = f"/results/raw_agentless/{iid}"
            localize_py = "/agentless/agentless/fl/localize.py"

            # choose dataset strategy
            # - simplest: always Verified
            # - optional: try Lite first, if file_level produces no output, retry Verified
            dataset_logic = ""
            if USE_FALLBACK:
                dataset_logic = (
                    f"DS={shlex.quote(FALLBACK_DATASET)}; "
                    "echo \"[dataset] try $DS\"; "
                )
            else:
                dataset_logic = f"DS={shlex.quote(DEFAULT_DATASET)}; echo \"[dataset] using $DS\"; "

            run_loc_cmd = (
                "set -e; cd /testbed; "
                "source /opt/miniconda3/etc/profile.d/conda.sh; "
                f"conda activate {shlex.quote(AGENTLESS_ENV)}; "
                "export PYTHONPATH=$PYTHONPATH:/agentless; "
                "export OPENAI_API_KEY=${OPENAI_API_KEY}; "
                "export HF_TOKEN=${HF_TOKEN:-}; "
                + dataset_logic +

                # helper to show diagnostics
                "tail_file(){ f=\"$1\"; n=\"${2:-120}\"; if [ -f \"$f\" ]; then echo \"--- tail $f ---\"; tail -n \"$n\" \"$f\"; fi; }; "

                # stage dirs
                f"mkdir -p {shlex.quote(out_base)}/file_level {shlex.quote(out_base)}/related "
                f"{shlex.quote(out_base)}/edit_location_samples {shlex.quote(out_base)}/edit_location_merged; "

                # ---- file_level (with tee) ----
                f"rm -f {shlex.quote(out_base)}/file_level/loc_outputs.jsonl; "
                f"python -u {localize_py} "
                f"--file_level "
                f"--dataset \"$DS\" "
                f"--target_id {shlex.quote(iid)} "
                f"--output_folder {shlex.quote(out_base)}/file_level "
                f"--num_threads 1 "
                f"2>&1 | tee {shlex.quote(out_base)}/file_level/stdout_stderr.txt; "

                # if no output, retry with Verified (only if fallback enabled)
                + (
                    f"if [ ! -f {shlex.quote(out_base)}/file_level/loc_outputs.jsonl ]; then "
                    f"  echo \"[WARN] file_level produced no loc_outputs.jsonl for dataset=$DS\"; "
                    f"  tail_file {shlex.quote(out_base)}/file_level/stdout_stderr.txt 200; "
                    f"  if [ \"$DS\" != {shlex.quote(DEFAULT_DATASET)} ]; then "
                    f"    DS={shlex.quote(DEFAULT_DATASET)}; "
                    f"    echo \"[dataset] retry $DS\"; "
                    f"    rm -f {shlex.quote(out_base)}/file_level/loc_outputs.jsonl; "
                    f"    python -u {localize_py} --file_level --dataset \"$DS\" "
                    f"      --target_id {shlex.quote(iid)} --output_folder {shlex.quote(out_base)}/file_level "
                    f"      --num_threads 1 2>&1 | tee {shlex.quote(out_base)}/file_level/stdout_stderr_retry.txt; "
                    f"  fi; "
                    f"fi; "
                    if USE_FALLBACK else ""
                ) +

                # hard fail if still missing
                f"if [ ! -f {shlex.quote(out_base)}/file_level/loc_outputs.jsonl ]; then "
                f"  echo \"[ERROR] file_level still missing loc_outputs.jsonl\" >&2; "
                f"  exit 10; "
                f"fi; "

                # ---- related_level ----
                f"python -u {localize_py} "
                f"--related_level "
                f"--dataset \"$DS\" "
                f"--target_id {shlex.quote(iid)} "
                f"--output_folder {shlex.quote(out_base)}/related "
                f"--top_n {TOP_N} "
                f"--compress "
                f"--start_file {shlex.quote(out_base)}/file_level/loc_outputs.jsonl "
                f"--num_threads {NUM_THREADS} "
                f"--skip_existing "
                f"2>&1 | tee {shlex.quote(out_base)}/related/stdout_stderr.txt; "

                f"if [ ! -f {shlex.quote(out_base)}/related/loc_outputs.jsonl ]; then "
                f"  echo \"[ERROR] related_level missing loc_outputs.jsonl\" >&2; "
                f"  exit 11; "
                f"fi; "

                # ---- fine_grain_line_level ----
                f"python -u {localize_py} "
                f"--fine_grain_line_level "
                f"--dataset \"$DS\" "
                f"--target_id {shlex.quote(iid)} "
                f"--output_folder {shlex.quote(out_base)}/edit_location_samples "
                f"--top_n {TOP_N} "
                f"--compress "
                f"--temperature {TEMPERATURE} "
                f"--num_samples {NUM_SAMPLES} "
                f"--start_file {shlex.quote(out_base)}/related/loc_outputs.jsonl "
                f"--num_threads {NUM_THREADS} "
                f"--skip_existing "
                f"2>&1 | tee {shlex.quote(out_base)}/edit_location_samples/stdout_stderr.txt; "

                f"if [ ! -f {shlex.quote(out_base)}/edit_location_samples/loc_outputs.jsonl ]; then "
                f"  echo \"[ERROR] fine_grain_line_level missing loc_outputs.jsonl\" >&2; "
                f"  exit 12; "
                f"fi; "

                # ---- merge ----
                f"python -u {localize_py} "
                f"--merge "
                f"--dataset \"$DS\" "
                f"--target_id {shlex.quote(iid)} "
                f"--output_folder {shlex.quote(out_base)}/edit_location_merged "
                f"--top_n {TOP_N} "
                f"--num_samples {NUM_SAMPLES} "
                f"--start_file {shlex.quote(out_base)}/edit_location_samples/loc_outputs.jsonl "
                f"2>&1 | tee {shlex.quote(out_base)}/edit_location_merged/stdout_stderr.txt; "

                # merge creates a differently named jsonl sometimes; pick newest jsonl in merged dir
                "MERGED=$(find "
                f"{shlex.quote(out_base)}/edit_location_merged "
                "-maxdepth 1 -type f -name '*.jsonl' -printf '%T@ %p\\n' | sort -nr | head -n 1 | cut -d' ' -f2-); "
                "if [ -z \"$MERGED\" ]; then echo '[ERROR] no merged jsonl found' >&2; exit 13; fi; "
                f"cp \"$MERGED\" /results/raw_agentless/{shlex.quote(iid)}.jsonl; "
                f"echo '--- merged output head ---'; head -n 3 /results/raw_agentless/{shlex.quote(iid)}.jsonl || true; "
            )

            print("\n[3/4] Run Agentless localization (Verified dataset, with checks)")
            try:
                run_in_container(container, run_loc_cmd)
            except Exception as e:
                # capture failure summary (stage inferred by exit code or message)
                append_failure({"instance_id": iid, "stage": "localize", "error": str(e)})
                print("[FAIL] localization failed; recorded in failures.jsonl")
                continue

            # [4/4] Host check
            host_stable = RAW_DIR / f"{iid}.jsonl"
            print("\n[4/4] Host check:", host_stable)
            if host_stable.exists():
                print("OK: wrote", host_stable)
            else:
                append_failure({"instance_id": iid, "stage": "host_check", "error": "missing stable jsonl on host"})
                print("[WARN] stable jsonl not found on host; recorded failure")

        finally:
            # If you want to debug, comment this line temporarily.
            container.remove(force=True)


if __name__ == "__main__":
    main()
