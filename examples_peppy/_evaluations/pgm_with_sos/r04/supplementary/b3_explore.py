# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import pgm_setup as mod

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
import sympy as sp

import pepflow as pf

REPO_ROOT = runtime.ROOT
certificate = json.loads((REPO_ROOT / "state/pgm_b2.json").read_text())
N_int = certificate["N_verify"]
params_sp = {"L": sp.Integer(1), "R": sp.Integer(1)}
ctx, pb, obj = mod.get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
workflow = (
    runtime.APPROVED
    / "plugins/pepflow-workflows/skills/lyap-define/references/workflow.md"
).read_text(encoding="utf-8")
checker = workflow.split("## Step 2")[1].split("```python")[1].split("```")[0]
(REPO_ROOT / "supplementary/b3_certificate_check.py").write_text(checker)
exec(checker)
f, g = mod.f, mod.g
exec(certificate["S_code"])
pieces, coefs, vecs = supplied_sos(ctx, N_int, 1)
S_piece_terms = {f"S_{i + 1}": piece for i, piece in enumerate(pieces)}
S_assignment = {name: i for i, name in enumerate(S_piece_terms)}
group_terms = {name: term for name, term in weighted_terms.items() if name != tau_name}
term_assignment = {}
for name in group_terms:
    left, right = name.split(":")[1].split(",")
    j = int(right[2:])
    term_assignment[name] = j - 1
lyap = [pf.Scalar.zero()]
partial_sum = sum(
    (term for name, term in group_terms.items() if term_assignment[name] == -1),
    pf.Scalar.zero(),
)
for step in range(N_int):
    partial_sum += sum(
        (term for name, term in group_terms.items() if term_assignment[name] == step),
        pf.Scalar.zero(),
    )
    partial_sum -= S_piece_terms[f"S_{step + 1}"]
    lyap.append(partial_sum)
ranks = []
svals = []
for k, v in enumerate(lyap):
    a = pm.eval_scalar(v).inner_prod_coords.astype(float)
    ranks.append(int(np.linalg.matrix_rank(a, tol=1e-4)))
    svals.append(np.linalg.svd(a, compute_uv=False).tolist())
    print("rank", k, ranks[-1])
    print("singular values", svals[-1])
observation = dict(
    N=N_int,
    certificate_id=certificate["certificate_id"],
    rank_profile=ranks,
    singular_values=svals,
    recipe_id="forward_star_consecutive_three_sos_per_step",
    boundary_exclusions={"left": 1, "right": 1},
    rank_convention={
        "tolerance": 1e-4,
        "scaling": "unscaled Gram coordinates",
        "order": "setup basis order",
    },
)
(REPO_ROOT / "supplementary/b3-rank-N4-initial.json").write_text(
    json.dumps(observation, indent=2)
)
coverage = workflow.split("## Step 6")[1].split("```python")[1].split("```")[0]
rank_tolerance = 1e-4
exec(coverage)
observation.update(
    certificate_checked=certificate_checked,
    grouping_checked=grouping_checked,
    rank_credible=True,
    term_assignment=term_assignment,
    S_assignment=S_assignment,
    boundary_constraints=boundary_names,
    boundary_S=boundary_S,
    sign_convention="Every increment is a sum of nonpositive interpolation residuals with nonnegative multipliers minus PSD square pieces; hence nonincreasing. Initial star,0 residual enters the first increment.",
)
(REPO_ROOT / "supplementary/b3-rank-N4-initial.json").write_text(
    json.dumps(observation, indent=2)
)
(REPO_ROOT / "supplementary/b3_coverage_check.py").write_text(coverage)
print("N4 checked; needs N6 certificate from B2 before cross-horizon confirmation")
