# Path constants
DATASET_PATH = "./datasets_refactor/dataset_out.json"
DATASET = "princeton-nlp/SWE-bench_Verified"
ASSERTFLIP_DIR = "./assertflip"
RESULTS_DIR = "./test_refactor"

# Other constants
max_attempts = 10
# model = "azure/gpt-4o"
model = "gpt-4o"
phase_mode = "pass_then_invert"  # Options: pass_then_invert (default mode), direct_fail_variant (for the ablations)
max_generation_retries = 10

# Refactor runner extra params (append only)
# ids list (json list[str] or list[{"instance_id": "..."}])
IDS_PATH = "./datasets_refactor/ids.json"

# directory containing <instance_id>.patch (or .diff)
PATCH_DIR = "./patches"

# refactor runner output dir mounted into container as /results
# (default keep same as RESULTS_DIR for perfect alignment with run_parallel)
REFACTOR_RESULTS_DIR = RESULTS_DIR

# where run_refactor_parallel writes extra logs (stderr/stdout of failing steps)
# keep inside REFACTOR_RESULTS_DIR so it's guaranteed to exist and be collected
REFACTOR_LOG_DIR = f"{REFACTOR_RESULTS_DIR}/logs_refactor"
