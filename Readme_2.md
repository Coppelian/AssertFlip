```bash
python ./scripts/run_refactor_parallel.py \
  --ids datasets_refactor/ids.json \
  --dataset datasets_refactor/dataset_out.json \
  --patch-dir patches \
  --out-dir outputs_refactor \
  --max-workers 1 \
  --timeout 600 \
  --seed 0
  --strategy all
```
