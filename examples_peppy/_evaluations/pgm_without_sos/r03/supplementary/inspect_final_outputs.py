import json
from pathlib import Path

b = json.loads(Path("pgm_example_lyap.ipynb").read_text())
for index in (2, 3):
    for line in "".join(b["cells"][index]["source"]).splitlines():
        if line.endswith("\\"):
            print(index, "trailing backslash count", len(line) - len(line.rstrip("\\")))
for i, c in enumerate(b["cells"]):
    if c["cell_type"] == "code":
        errors = [o for o in c["outputs"] if o["output_type"] == "error"]
        assert c["execution_count"] is not None and not errors, (i, errors)
        if i >= 26:
            output = "".join("".join(o.get("text", [])) for o in c["outputs"])
            print(i, output[-500:])
