import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import configure,NOTEBOOK_DIR
configure()
import json
from derive_coefficients import derive
e,unknowns,equations,solved,free,substitution=derive()
print("Equations",len(equations),"Unknowns",len(unknowns),"free",sorted(map(str,free)))
for u,v in zip(unknowns,solved):
    print(u,"=",v)
record={"equations":[str(v) for v in equations],"solution":{str(u):str(v) for u,v in zip(unknowns,solved)},
"free_symbols":sorted(map(str,free)),"chosen_solution":{str(u):str(v) for u,v in substitution.items()}}
(NOTEBOOK_DIR/"supplementary/b5-coefficient-derivation.json").write_text(json.dumps(record,indent=2))

