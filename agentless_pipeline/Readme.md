```bash
python convert_agentless_to_9refactor_schema.py \
  --ids ids.json \
  --schema_template Agentless_9Refactor_schema_template.json \
  --agentless_root /home/coppelia/program/AssertFlip/agentless_pipeline/out/raw_agentless \
  --source_root /home/coppelia/program/manual_craft/tmp \
  --verified_path SWE-bench_Verified.jsonl \
  --merged_mode all \
  --out_json ./out_agentless_like_9refactor.json \
  --out_jsonl ./out_agentless_like_9refactor.jsonl
```