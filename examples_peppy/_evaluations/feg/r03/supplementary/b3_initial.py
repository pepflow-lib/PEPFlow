# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
import sympy as sp
from feg_setup import get_pep_setup

ROOT = runtime.ROOT
workflow = (
    ROOT
    / "supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md"
).read_text(encoding="utf-8")
certificate_check_code = workflow.split("```python\nimport hashlib\n", 1)[1].split(
    "```", 1
)[0]
certificate_check_code = "import hashlib\n" + certificate_check_code
certificate_check_code = certificate_check_code.replace(
    "(REPO_ROOT / relative_path).resolve()", "(notebook_dir / relative_path).resolve()"
).replace(
    "source_path.is_relative_to(REPO_ROOT)", "source_path.is_relative_to(notebook_dir)"
)
(ROOT / "supplementary/b3_certificate_check.py").write_text(certificate_check_code)
decomposition_code = """# Retain the whole coherent PSD remainder as one terminal PSD block.
# B2's candidate square was compared but is not substituted for saved S.
D = np.asarray(certificate["numerical_decomposition"]["D"],dtype=float)
E = np.asarray(certificate["numerical_decomposition"]["ell_coords"],dtype=float)
ell = [sum((float(c)*v for c,v in zip(row,basis)),pf.Vector.zero()) for row in E]
full_S = sum((float(D[i,j])*ell[i]*ell[j] for i,j in np.ndindex(D.shape)),pf.Scalar.zero())
assert np.allclose(E.T@D@E,S_array,atol=tol["reconstruction_atol"],rtol=tol["reconstruction_rtol"])
S_piece_terms = {"terminal_PSD_remainder": full_S}
"""
(ROOT / "supplementary/b3_decomposition.py").write_text(decomposition_code)
grouping_code = """grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
# Residuals are <=0 and multipliers nonnegative, so increments are <=0.
group_terms = {name:term for name,term in weighted_terms.items() if name!=tau_name}
term_assignment = {}
for name in group_terms:
    if name == f"A monotone:x_{N_int},x_star":
        term_assignment[name] = "boundary"
    for k in range(N_int):
        half = "x_1/2" if k==0 else f"x_{k}+1/2"
        lip_pair = f"x_1,{half}" if k==0 else f"{half},x_{k+1}"
        if name == f"A Lipschitz:{lip_pair}":
            term_assignment[name] = k
        if k>=1 and name == f"A monotone:x_{k},x_{k+1}":
            term_assignment[name] = k
assert set(term_assignment)==set(group_terms)
S_assignment = {"terminal_PSD_remainder":"boundary"}
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for k in range(N_int):
    partial_sum += sum((group_terms[name] for name,step in term_assignment.items() if step==k),pf.Scalar.zero())
    partial_sum -= sum((S_piece_terms[name] for name,step in S_assignment.items() if step==k),pf.Scalar.zero())
    lyap.append(partial_sum)
ranks=[]
singular_values=[]
for k,Vk in enumerate(lyap):
    matrix=np.asarray(pm.eval_scalar(Vk).inner_prod_coords,dtype=float)
    values=np.linalg.svd(matrix,compute_uv=False)
    rank=int(np.sum(values>rank_tolerance))
    ranks.append(rank)
    singular_values.append(values.tolist())
    print(f"rank V_{k}: {rank}")
    if k==0:
        print()
retained_ranks=ranks[rank_left:N_int+1-rank_right]
print("Interior rank is constant at this N:",len(retained_ranks)>=3 and len(set(retained_ranks))==1,"boundary exclusions:",(rank_left,rank_right))
"""
coverage = workflow.split("```python\nboundary_names =", 1)[1].split("```", 1)[0]
grouping_code += "\nboundary_names =" + coverage
(ROOT / "supplementary/b3_grouping.py").write_text(grouping_code)
certificate = json.loads((ROOT / "state/feg_b2.json").read_text())
N_int = certificate["N_verify"]
N = sp.S(N_int)
params_sp = {k: sp.S(v) for k, v in json.loads(certificate["params_json"]).items()}
REPO_ROOT = ROOT / "supplementary/approved"
notebook_dir = ROOT
ctx, pb, obj = get_pep_setup(N, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
ctx.set_as_current()
exec(certificate_check_code)
exec(decomposition_code)
exec(grouping_code)
profile = dict(
    N=N_int,
    certificate_id=certificate["certificate_id"],
    recipe_id="consecutive_monotone_and_halfstep_lipschitz_terminal_S_v1",
    rank_profile=ranks,
    singular_values=singular_values,
    rank_convention=dict(
        tolerance=1e-4,
        scaling="none; absolute tolerance on original Gram coordinates",
        coordinate_order="setup earlier iterates first",
    ),
    rank_credible=all(
        not (0.5e-4 <= v <= 2e-4) for values in singular_values for v in values
    ),
    certificate_checked=certificate_checked,
    grouping_checked=grouping_checked,
    boundary_exclusions=dict(left=1, right=1),
    term_assignment=term_assignment,
    S_assignment=S_assignment,
    lyap_inner_prod_coords=[
        np.asarray(pm.eval_scalar(v).inner_prod_coords, dtype=float).tolist()
        for v in lyap
    ],
    lyap_func_coords=[
        np.asarray(pm.eval_scalar(v).func_coords, dtype=float).tolist() for v in lyap
    ],
    lyap_offsets=[float(pm.eval_scalar(v).offset) for v in lyap],
)
(ROOT / "supplementary/b3-rank-N4.json").write_text(json.dumps(profile, indent=2))
(ROOT / "supplementary/b3-continuation.json").write_text(
    json.dumps(
        dict(
            current_block="B3",
            completion_status="incomplete",
            next_block="B2",
            requested_horizon=6,
            reason="N4 rank and coverage pass; obtain a coherent N6 certificate for required cross-horizon confirmation",
            selected_certificate_id=certificate["certificate_id"],
        ),
        indent=2,
    )
)
print("Singular values:", json.dumps(singular_values))
