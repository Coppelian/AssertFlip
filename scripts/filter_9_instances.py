import json

TARGET = {
  "astropy__astropy-7606",
  "astropy__astropy-8707",
  "astropy__astropy-8872",
  "astropy__astropy-12907",
  "astropy__astropy-13977",
  "django__django-10097",
  "matplotlib__matplotlib-20488",
  "matplotlib__matplotlib-25479",
  "scikit-learn__scikit-learn-26194",
}

IN_PATH  = "../datasets/SWT_Verified_Agentless_Test_Source_Skeleton.json"
OUT_PATH = "../datasets/SWT_Verified_Agentless_9Refactor.json"

with open(IN_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

out = [x for x in data if x.get("instance_id") in TARGET]

missing = TARGET - {x["instance_id"] for x in out}
print("selected:", len(out))
print("missing:", sorted(missing))

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("wrote:", OUT_PATH)
