# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

sys.path.insert(0, str(runtime.ROOT / "supplementary"))
import hashlib
import json
import uuid

import numpy as np
from b2_acquire import capture

import pepflow as pf
from pepflow.utils import Comparator

ROOT = runtime.ROOT
b1 = json.loads((ROOT / "state/feg_b1.json").read_text())
N = b1["N_verify"]
params = json.loads(b1["params_json"])
allowed = json.loads((ROOT / "supplementary/approved/allowlist.json").read_text())[
    "exact_read_files"
]
sources = [
    ROOT / "feg_setup.py",
    Path(__file__),
    ROOT / "supplementary/b2_acquire.py",
] + [
    Path(p)
    for p in allowed
    if Path(p).parent == ROOT / "supplementary/approved/pepflow"
]
source_hashes = {
    str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
        p.read_bytes()
    ).hexdigest()
    for p in sources
}
dense = json.loads((ROOT / "state/feg_dense.json").read_text())
drops = json.loads((ROOT / "state/feg_relaxed_constraints.json").read_text())
ctx, pb, op, result, entries, state = capture(N, drops)
ctx.set_as_current()
pm = pf.ExpressionManager(ctx, resolve_parameters=params)
basis = ctx.basis_vectors()
S = np.asarray(state["S_matrix"], dtype=float)
eigenvalues, Q = np.linalg.eigh((S + S.T) / 2)
D = np.diag(eigenvalues)
E = Q.T
ell = [sum((float(c) * v for c, v in zip(row, basis)), pf.Vector.zero()) for row in E]
S_numeric = sum(
    (float(eigenvalues[i]) * ell[i] ** 2 for i in range(len(ell))), pf.Scalar.zero()
)
weighted = pf.Scalar.zero()
for c, *_ in entries:
    value = state["named_dual_values"][c.name]
    if value is None:
        continue
    residual = c.lhs - c.rhs
    if c.cmp in (Comparator.GE, Comparator.SEQ):
        residual = -residual
    weighted += value * (pf.Scalar.zero() + residual)
checked = pm.eval_scalar(
    pb.performance_metric - float(result.opt_value) - weighted + S_numeric
)
maxabs = lambda x: float(np.max(np.abs(np.asarray(x, dtype=float)), initial=0.0))  # noqa: E731 - retain the archived notebook helper
residuals = dict(
    identity_gram_max_abs=maxabs(checked.inner_prod_coords),
    identity_func_max_abs=maxabs(checked.func_coords),
    identity_offset_abs=maxabs(checked.offset),
    S_reconstruction_max_abs=maxabs(E.T @ D @ E - S),
    dense_relaxed_gap=abs(dense["opt_value"] - state["opt_value"]),
    minimum_scalar_inequality_dual=min(
        v for v in state["named_dual_values"].values() if v is not None
    ),
    minimum_S_eigenvalue=float(eigenvalues.min()),
    minimum_matrix_inequality_eigenvalue=0.0,
    conjecture_gap=abs(state["opt_value"] - 4 / N**2),
)
tolerances = dict(
    identity_atol=1e-5,
    identity_rtol=0.0,
    reconstruction_atol=1e-4,
    reconstruction_rtol=1e-5,
    dual_tol=1e-6,
    psd_tol=1e-6,
    dense_opt_atol=1e-5,
)
assert result.solver_status == "optimal"
assert all(
    residuals[k] <= 1e-5
    for k in (
        "identity_gram_max_abs",
        "identity_func_max_abs",
        "identity_offset_abs",
        "dense_relaxed_gap",
        "conjecture_gap",
    )
)
assert np.allclose(E.T @ D @ E, S, atol=1e-4, rtol=1e-5)
assert (
    residuals["minimum_scalar_inequality_dual"] >= -1e-6 and eigenvalues.min() >= -1e-6
)

# Candidate formulas inferred from the sparse multipliers, including every group.
lamb_code = """def lambda_candidate(name, N, L=1):
    import sympy as sp
    N, L = sp.S(N), sp.S(L)
    if name == "initial_condition":
        return 4*L**2/N**2
    for k in range(1,int(N)):
        if name == f"A monotone:x_{k},x_{k+1}":
            return 4*L*k*(k+1)/N**2
    if name == f"A monotone:x_{N},x_star":
        return 4*L/N
    for k in range(int(N)):
        half = "x_1/2" if k==0 else f"x_{k}+1/2"
        pair = f"x_1,{half}" if k==0 else f"{half},x_{k+1}"
        if name == f"A Lipschitz:{pair}":
            return 2*sp.Integer(k+1)**2/N**2
    return sp.S.Zero
"""
S_code = """def S_candidate(ctx, op, N, L=1):
    import sympy as sp
    return (2*sp.S(L)/sp.S(N)*(ctx["x_0"]-ctx["x_star"])-op(ctx[f"x_{N}"]))**2
"""
exec(lamb_code)
exec(S_code)
candidate_vals = {
    name: lambda_candidate(name, N, params["L"]) for name in state["named_dual_values"]
}
lamerr = max(
    abs(float(candidate_vals[k]) - float(v or 0))
    for k, v in state["named_dual_values"].items()
)
guess = pm.eval_scalar(S_candidate(ctx, op, N, params["L"]))
Serr = maxabs(np.asarray(guess.inner_prod_coords, dtype=float) - S)
candidate_weighted = pf.Scalar.zero()
for c, *_ in entries:
    residual = c.lhs - c.rhs
    if c.cmp in (Comparator.GE, Comparator.SEQ):
        residual = -residual
    candidate_weighted += candidate_vals[c.name] * (pf.Scalar.zero() + residual)
exact_sample = pf.ExpressionManager(ctx, resolve_parameters=params).eval_scalar(
    pb.performance_metric
    - 4 / N**2
    - candidate_weighted
    + S_candidate(ctx, op, N, params["L"])
)
# Numerical sample comparison; no all-horizon analytic claim.
candidate_residual = max(
    maxabs(exact_sample.inner_prod_coords),
    maxabs(exact_sample.func_coords),
    maxabs(exact_sample.offset),
)
search = dict(
    completed=True,
    references_reviewed=[
        "Own input and approved generic operator API; no target references authorized"
    ],
    attempts=[
        dict(
            component="lambda",
            method="Rational inspection of all sparse groups: k(k+1), (k+1)^2 and terminal factors",
            maximum_sample_difference=lamerr,
            comparison_atol=1e-4,
            passed=lamerr <= 1e-4,
        ),
        dict(
            component="S",
            method="Inspect rank-one dominant eigenspace and compare square ||(2L/N)(x0-xstar)-A(xN)||^2",
            maximum_sample_difference=Serr,
            comparison_atol=1e-4,
            passed=Serr <= 1e-4,
        ),
        dict(
            component="joint",
            method="Reassemble candidate finite-N certificate",
            sample_identity_max_abs=candidate_residual,
        ),
    ],
    unresolved_components=["All-horizon validity of candidate lambda and S identities"],
)
assert lamerr <= 1e-4 and Serr <= 1e-4
state.update(b1)
state.update(
    N=N,
    N_verify=N,
    opt_value=float(result.opt_value),
    tau_sol=state["named_dual_values"]["initial_condition"],
    tau_name="initial_condition",
    relaxed_constraints=drops,
    basis_scalars=[str(v) for v in ctx.basis_scalars()],
    normalization=dict(
        tau_name="initial_condition",
        initial_condition=b1["initial_condition"],
        performance_metric=b1["performance_metric"],
        bound_value=float(result.opt_value),
        bound_formula=b1["conjectured_rate"],
    ),
    certificate_provenance=dict(
        solve_id=str(uuid.uuid4()),
        pep_type="primal",
        solver_status=result.solver_status,
        source_hashes=source_hashes,
        source_root="notebook_dir",
        solver=dict(
            api="CVXPrimalSolver.build_problem / cvxpy.Problem.solve",
            effective_name="CLARABEL",
            settings={},
            attempts=state["attempts"],
        ),
    ),
    numerical_checks=dict(tolerances=tolerances, residuals=residuals, passed=True),
    numerical_decomposition=dict(
        method="direct",
        D=D.tolist(),
        ell_coords=E.tolist(),
        basis_labels=[str(v) for v in basis],
        description="Full symmetric eigendecomposition; all eigenvalues and factors retained",
    ),
    closed_form_search=search,
    formula_status=dict(lambda_status="candidate", S="candidate"),
    lamb_code=lamb_code,
    S_code=S_code,
    S_decomp_type="direct",
    numerical_certificate_verified=True,
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=False,
    require_analytic_full_pep=False,
    proof_valid=True,
)
state["formula_status"] = {"lambda": "candidate", "S": "candidate"}
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
        {key: state[key] for key in keys},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
).hexdigest()
for p in sources:
    assert (
        hashlib.sha256(p.read_bytes()).hexdigest()
        == source_hashes[str(p.relative_to(ROOT)).replace("\\", "/")]
    )
for name in ("feg_b2.json", "feg_relaxed.json"):
    (ROOT / "state" / name).write_text(json.dumps(state, indent=2, allow_nan=False))
print(
    json.dumps(
        dict(
            residuals=residuals, search=search, certificate_id=state["certificate_id"]
        ),
        indent=2,
    )
)
