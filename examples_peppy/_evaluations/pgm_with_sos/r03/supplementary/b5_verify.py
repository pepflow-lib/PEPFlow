import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import configure,NOTEBOOK_DIR
configure()
import json
from exact_proof import (local_context,potential,terminal_potential,step_rhs,
    base_rhs,terminal_rhs,single_rhs,check_identity,K,NN,symbolic_values)
checks=[]
e=local_context("step")
checks.append(check_identity("step",potential(e,e["y"],K+1)-potential(e,e["x"],K),step_rhs(e,K),e,display=False))
print("Step passed",flush=True)
e=local_context("base",base=True)
checks.append(check_identity("base",potential(e,e["y"],1),base_rhs(e),e,display=False))
print("Base passed",flush=True)
e=local_context("boundary")
checks.append(check_identity("boundary",terminal_potential(e)-potential(e,e["x"],NN-1),terminal_rhs(e),e,display=False))
print("Boundary passed",flush=True)
e=local_context("single",base=True)
checks.append(check_identity("N=1",terminal_potential(e),single_rhs(e),e,
                            values={**symbolic_values,"N":__import__("sympy").S.One},display=False))
print("N=1 passed",flush=True)
(NOTEBOOK_DIR/"supplementary/b5-exact-identities.json").write_text(json.dumps(checks,indent=2))

