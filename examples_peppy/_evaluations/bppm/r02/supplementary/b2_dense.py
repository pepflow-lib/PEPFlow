from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
from runtime import ATTEMPT, solve_explicit
import json
import numpy as np
from bppm_setup import get_pep_setup

ctx, pb, obj = get_pep_setup(4, {})
result, attempts = solve_explicit(ctx, pb, {"alpha": 1, "R": 1})
groups = {}
for owner in ctx.func_to_triplets:
    groups[str(owner)] = {c.name: float(result.get_dual_value(c.name)) for c in owner.get_interpolation_constraints(ctx)}
S = result.get_gram_dual_matrix()
data = {"N": 4, "opt_value": float(result.opt_value), "solver_attempts": attempts,
        "all_owner_duals": groups, "S_matrix": S.matrix.tolist(), "S_row_names": S.row_names,
        "basis_vectors": [str(v) for v in ctx.basis_vectors()]}
(ATTEMPT / "state/bppm_dense.json").write_text(json.dumps(data, indent=2))
print("dense optimum", result.opt_value, "S eigenvalues", np.linalg.eigvalsh(S.matrix))
for owner, duals in groups.items():
    print(owner, {k: round(v, 7) for k,v in duals.items() if abs(v)>1e-6})
