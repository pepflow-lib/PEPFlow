import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import configure,NOTEBOOK_DIR
configure()
import json
from grouping import construct
state=json.loads((NOTEBOOK_DIR/"state/pgm_b2.json").read_text())
ctx,pb,lyap,sample=construct(state)
(NOTEBOOK_DIR/"supplementary/b3-N4-trial.json").write_text(json.dumps(sample,indent=2))
print("Coverage residual:",sample["coverage_residual"])
print("Singular values:",sample["singular_values"])

