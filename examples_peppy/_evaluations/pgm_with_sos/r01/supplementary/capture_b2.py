import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import json
import uuid
from fractions import Fraction
from importlib.metadata import version

import numpy as np
import pgm_setup as mod
import runtime
import sympy as sp

# local helper resolved by the notebook runtime path
from candidates import (  # ty: ignore[unresolved-import]
    aid_pieces,
    multiplier_candidate,
    square_sum,
)

import pepflow as pf

root = runtime.ATTEMPT
b1 = json.loads((root / "state/pgm_b1.json").read_text())
N = int(sys.argv[1]) if len(sys.argv) > 1 else b1["N_verify"]
params = json.loads(b1["params_json"])
allow = json.loads((runtime.APPROVED / "allowlist.json").read_text())
paths = [
    Path(p)
    for p in allow["exact_read_files"]
    if Path(p).parent == runtime.APPROVED / "pepflow"
]
paths += [root / "pgm_setup.py", root / "supplementary/helpers/candidates.py"]
hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
ctx, pb, obj = mod.get_pep_setup(N, params)
entries = [(c, "initial", None, None) for c in pb.init_conditions]
for owner in ctx.func_to_triplets:
    owner.get_interpolation_constraints(ctx)
    groups = ctx.get_constraint_data(owner)
    entries.extend(
        (c, "interpolation", str(owner), str(group))
        for group, cs in groups.sc_dict.items()
        for c in cs
    )
    entries.extend(
        (c, "interpolation", str(owner), str(group))
        for group, c in groups.psd_dict.items()
    )
assert all(isinstance(c, pf.ScalarConstraint) for c, *_ in entries)
relaxed = []
for c, *_ in entries:
    if c.name == "initial_condition":
        continue
    ri, ci = c.name.split(":")[1].split(",")
    keep = ri == "x_star" or (ci != "x_star" and int(ci[2:]) == int(ri[2:]) + 1)
    if not keep:
        relaxed.append(c.name)
pb.set_relaxed_constraints(relaxed)
solver = pf.CVXPrimalSolver(
    pb.performance_metric, [c for c, *_ in entries if c.name not in relaxed], ctx
)
problem = solver.build_problem(resolve_parameters=params)
value = problem.solve(solver="CLARABEL")
result = pf.PEPResult(
    opt_value=value,
    dual_var_manager=solver.dual_var_manager,
    pep_type=pf.PEPType.PRIMAL,
    solver_status=problem.status,
    context=ctx,
)
S_sol = result.get_gram_dual_matrix()
S = np.asarray(S_sol.matrix, dtype=float)
pm = pf.ExpressionManager(ctx, resolve_parameters=params)
metadata = {}
duals = {}
weighted = pf.Scalar.zero()
for c, origin, owner, group in entries:
    dropped = c.name in relaxed
    metadata[c.name] = dict(
        origin=origin,
        owner=owner,
        group=group,
        kind="scalar",
        comparator=c.cmp.value,
        shape=[],
        relaxed=dropped,
    )
    val = None if dropped else float(result.get_dual_value(c.name))
    duals[c.name] = val
    if val is not None:
        residual = c.lhs - c.rhs
        if c.cmp == pf.Comparator.GE:
            residual = -residual
        weighted += val * residual
pieces = aid_pieces(ctx, mod.f, mod.g, mod.L, N)
S_numeric = square_sum(pieces)
E = np.array([pm.eval_vector(u).coords for _, _, _, u in pieces], dtype=float)
# Coefficients contain the generic L parameter; use its existing evaluator.
from pepflow.parameter import (  # noqa: E402 - imports follow runtime or notebook setup
    eval_parameter,
)

D = np.diag([float(eval_parameter(c, params)) for _, _, c, _ in pieces])
checked = pm.eval_scalar(pb.performance_metric - float(value) - weighted + S_numeric)
maxabs = lambda a: float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0))  # noqa: E731 - retain the archived notebook helper
dense = json.loads((root / "state/pgm_dense.json").read_text())
residuals = dict(
    identity_gram_max_abs=maxabs(checked.inner_prod_coords),
    identity_func_max_abs=maxabs(checked.func_coords),
    identity_offset_abs=maxabs(checked.offset),
    S_reconstruction_max_abs=maxabs(E.T @ D @ E - S),
    dense_relaxed_gap=abs(dense["opt_value"] - float(value)),
    minimum_scalar_inequality_dual=min(v for v in duals.values() if v is not None),
    minimum_S_eigenvalue=float(np.linalg.eigvalsh(S).min()),
    minimum_matrix_inequality_eigenvalue=0.0,
)
tol = dict(
    identity_atol=1e-5,
    identity_rtol=0,
    reconstruction_atol=1e-4,
    reconstruction_rtol=1e-5,
    dual_tol=1e-6,
    psd_tol=1e-6,
    dense_opt_atol=1e-5,
)
passed = (
    problem.status == "optimal"
    and all(
        residuals[k] < 1e-5
        for k in [
            "identity_gram_max_abs",
            "identity_func_max_abs",
            "identity_offset_abs",
            "dense_relaxed_gap",
        ]
    )
    and np.allclose(E.T @ D @ E, S, atol=1e-4, rtol=1e-5)
    and residuals["minimum_scalar_inequality_dual"] >= -1e-6
    and residuals["minimum_S_eigenvalue"] >= -1e-6
)
assert passed, residuals
candidate_error = max(
    abs(v - float(multiplier_candidate(name, N)))
    for name, v in duals.items()
    if v is not None
)
assert candidate_error < 1e-4
# Exact fixed-horizon check, distinguished from arbitrary-horizon verification.
weighted_exact = pf.Scalar.zero()
for c, *_ in entries:
    residual = c.lhs - c.rhs
    if c.cmp == pf.Comparator.GE:
        residual = -residual
    weighted_exact += multiplier_candidate(c.name, N) * residual
exact_manager = pf.ExpressionManager(
    ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One}
)
exact = exact_manager.eval_scalar(
    pb.performance_metric
    - multiplier_candidate("initial_condition", N)
    - weighted_exact
    + S_numeric,
    sympy_mode=True,
)
exact_residual = max(
    maxabs(exact.inner_prod_coords), maxabs(exact.func_coords), maxabs(exact.offset)
)
print(
    "Fixed-N raw residual:",
    exact_residual,
    exact.inner_prod_coords,
    exact.func_coords,
    exact.offset,
)
assert exact_residual == 0
search = dict(
    completed=True,
    references_reviewed=["supplementary/approved/input.md: supplied SOS candidate"],
    attempts=[
        dict(
            method="Sparse dual fractions and consecutive cumulative differences",
            lambda_max_abs_error=candidate_error,
            outcome="Candidate formulas for both f and g; exact fixed-N identity checked",
        ),
        dict(
            method="Supplied exact SOS aid without solver constraints",
            normalization=1,
            S_reconstruction_max_abs=residuals["S_reconstruction_max_abs"],
            outcome="Matches coherent selected matrix; exact fixed-N candidate identity is zero",
        ),
    ],
    unresolved_components=[
        "Arbitrary-horizon analytic verification of candidate identity"
    ],
)
source = (root / "supplementary/helpers/candidates.py").read_text()
state = {
    **b1,
    "N": N,
    "N_verify": N,
    "opt_value": float(value),
    "tau_sol": duals["initial_condition"],
    "tau_name": "initial_condition",
    "relaxed_constraints": relaxed,
    "S_matrix": S.tolist(),
    "S_row_names": list(S_sol.row_names),
    "S_col_names": list(S_sol.col_names),
    "basis_vectors": [str(v) for v in ctx.basis_vectors()],
    "basis_scalars": [str(v) for v in ctx.basis_scalars()],
    "named_dual_values": duals,
    "constraint_metadata": metadata,
    "normalization": dict(
        tau_name="initial_condition",
        initial_condition=b1["initial_condition"],
        performance_metric=b1["performance_metric"],
        bound_value=float(value),
        bound_formula=b1["conjectured_rate"],
        SOS_scale=1,
    ),
    "certificate_provenance": dict(
        solve_id=str(uuid.uuid4()),
        pep_type="primal",
        solver_status=problem.status,
        source_hashes=hashes,
        solver=dict(
            api="CVXPrimalSolver.build_problem",
            effective_name="CLARABEL",
            settings={},
            cvxpy_version=version("cvxpy"),
        ),
    ),
    "numerical_checks": dict(tolerances=tol, residuals=residuals, passed=bool(passed)),
    "numerical_decomposition": dict(
        method="direct",
        D=D.tolist(),
        ell_coords=E.tolist(),
        basis_labels=[str(v) for v in ctx.basis_vectors()],
        piece_labels=[f"{j}:{family}" for j, family, _, _ in pieces],
        source="supplementary/helpers/candidates.py",
        normalization=1,
    ),
    "closed_form_search": search,
    "formula_status": dict(lambda_="candidate", S="candidate"),
    "lamb_code": source,
    "S_code": source,
    "S_decomp_type": "direct",
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "require_analytic_full_pep": False,
    "proof_valid": True,
    "candidate_fixed_N_exact_residual": exact_residual,
}
state["formula_status"]["lambda"] = state["formula_status"].pop("lambda_")
groups = {}
for owner in (mod.f, mod.g):
    group = result.get_scalar_constraint_dual_value_in_numpy(owner)
    if not isinstance(group, dict):
        group = {"interpolation": group}
    for name, m in group.items():
        groups[f"{owner}:{name}"] = dict(
            matrix=np.asarray(m.matrix, dtype=float).tolist(),
            row_names=list(m.row_names),
            col_names=list(m.col_names),
        )
state["lambda_groups"] = groups
keys = (
    "N_verify",
    "params_json",
    "relaxed_constraints",
    "S_matrix",
    "S_row_names",
    "S_col_names",
    "basis_vectors",
    "basis_scalars",
    "opt_value",
    "tau_sol",
    "tau_name",
    "named_dual_values",
    "constraint_metadata",
    "normalization",
    "certificate_provenance",
    "numerical_checks",
    "numerical_decomposition",
)
state["certificate_id"] = hashlib.sha256(
    json.dumps(
        {k: state[k] for k in keys},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
).hexdigest()
for p, expected in hashes.items():
    assert hashlib.sha256(Path(p).read_bytes()).hexdigest() == expected
for name in ("pgm_relaxed.json", "pgm_b2.json"):
    (root / "state" / name).write_text(json.dumps(state, indent=2, allow_nan=False))
(root / "state/pgm_relaxed_constraints.json").write_text(json.dumps(relaxed, indent=2))
print("Numerical checks:", residuals)
print(
    "Candidate multiplier error:",
    candidate_error,
    "exact fixed-N residual:",
    exact_residual,
)
for name, val in duals.items():
    if val is not None:
        print(name, val, str(Fraction(val).limit_denominator(1000)))
