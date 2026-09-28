# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np
import runtime
import sympy as sp
from pgm_setup import get_pep_setup

import pepflow as pf

notebook_dir = runtime.ATTEMPT
REPO_ROOT = runtime.APPROVED
certificate = json.loads((notebook_dir / "state/pgm_b2.json").read_text())
N_int = certificate["N_verify"]
params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.S.One, "R": sp.S.One}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
workflow = (
    runtime.APPROVED
    / "plugins/pepflow-workflows/skills/lyap-define/references/workflow.md"
).read_text(encoding="utf-8-sig")
code = next(
    chunk.split("```")[0]
    for chunk in workflow.split("```python\n")[1:]
    if "certificate_checked = False" in chunk.split("```")[0]
)
code = code.replace(
    "(REPO_ROOT / relative_path)", "(notebook_dir / relative_path)"
).replace(
    "source_path.is_relative_to(REPO_ROOT)", "source_path.is_relative_to(notebook_dir)"
)
(notebook_dir / "supplementary/b3_certificate_check.py").write_text(code)
exec(compile(code, "b3_certificate_check.py", "exec"))
D = np.asarray(certificate["numerical_decomposition"]["D"], float)
E = np.asarray(certificate["numerical_decomposition"]["ell_coords"], float)
assert np.allclose(D, np.diag(np.diag(D)), atol=0, rtol=0)
# Exploratory full-coordinate arrays preserve every numerical factor and multiplier.
terms = {name: pm.eval_scalar(term) for name, term in interpolation_terms.items()}
term_steps = {name: int(name.split(",")[1][2:]) - 1 for name in terms}
trials = []
for shift in (-1, 0, 1):
    assignment = {}
    for i in range(len(D)):
        largest_iteration = N_int - i // 2 if i < 2 * N_int else 0
        assignment[i] = min(N_int - 1, max(-1, largest_iteration - 1 + shift))
    mats = [np.zeros_like(S_array)]
    partial = np.zeros_like(S_array)
    for k in range(N_int):
        indices = {-1, 0} if k == 0 else {k}
        for name, term in terms.items():
            if term_steps[name] in indices:
                partial += np.asarray(term.inner_prod_coords, float)
        for i, step in assignment.items():
            if step in indices:
                partial -= D[i, i] * np.outer(E[i], E[i])
        mats.append(partial.copy())
    singular = [np.linalg.svd(mat, compute_uv=False).tolist() for mat in mats]
    ranks = [int(np.sum(np.array(s) > 1e-4)) for s in singular]
    trial = dict(
        recipe="reverse_ldl_latest_iteration",
        shift=shift,
        ranks=ranks,
        singular_values=singular,
        S_assignment=assignment,
    )
    trials.append(trial)
    print("shift", shift, "ranks", ranks)
(notebook_dir / "supplementary/b3-n4-initial-trials.json").write_text(
    json.dumps(trials, indent=2)
)
