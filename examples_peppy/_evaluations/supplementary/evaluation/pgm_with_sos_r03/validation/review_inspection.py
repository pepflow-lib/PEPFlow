import json
from pathlib import Path

root = Path.cwd()
nb = json.loads((root / "pgm_example_lyap.ipynb").read_text(encoding="utf-8"))
r = json.loads((root / "review-replay.json").read_text(encoding="utf-8"))
audit = {
    "saved_notebook_code_cells": sum(c["cell_type"] == "code" for c in nb["cells"]),
    "saved_notebook_execution_counts": [
        c["execution_count"] for c in nb["cells"] if c["cell_type"] == "code"
    ],
    "saved_cell_errors": [
        (c["id"], o.get("ename"))
        for c in nb["cells"]
        for o in c.get("outputs", [])
        if o["output_type"] == "error"
    ],
    "plot_output_present": any(
        "image/png" in o.get("data", {})
        for c in nb["cells"]
        for o in c.get("outputs", [])
    ),
    "static": {},
}
for filename in [
    "b1-static-003.json",
    "b2-static-003.json",
    "b3-transport-static-002.json",
    "b4-static-002.json",
    "b5-static-002.json",
]:
    d = json.loads((root / "supplementary" / filename).read_text(encoding="utf-8"))
    audit["static"][filename] = {
        "status": d["status"],
        "checks": [
            {k: c.get(k) for k in ("label", "returncode", "stdout", "stderr")}
            for c in d["commands"]
            if c["label"] in ("source_ruff", "source_ty")
        ],
    }
audit["rank_separation"] = []
for row in r["rank_samples"]:
    vals = [v for sv in row["singular_values"] for v in sv]
    audit["rank_separation"].append(
        {
            "N": row["N"],
            "max_below_cutoff": max(v for v in vals if v < 1e-4),
            "min_above_cutoff": min(v for v in vals if v > 1e-4),
        }
    )
audit["N6_saved_certificate_checks"] = json.loads(
    (root / "supplementary/N6-selected/pgm_b2.json").read_text()
)["numerical_checks"]
(root / "review-delivery-inspection.json").write_text(
    json.dumps(audit, indent=2), encoding="utf-8"
)
print(json.dumps(audit, indent=2))
