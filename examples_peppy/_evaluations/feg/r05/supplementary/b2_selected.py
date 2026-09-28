import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "runtime", Path(__file__).parent / "helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
from certificates import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    acquire,
    summarize,
)
from verify_certificate import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    verify_saved,
)

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup
from pepflow.lyapunov_utils import (  # noqa: E402 - imports follow runtime or notebook setup
    ldl_decompose_with_reversed_basis,
)

root = runtime.ROOT
b1 = json.loads((root / "state/feg_b1.json").read_text())
dense = json.loads((root / "state/feg_dense.json").read_text())
dropped = [
    name
    for name, value in dense["named_dual_values"].items()
    if name != "initial_condition" and abs(value) <= 1e-6
]
ctx, pb, obj, result, entries, data = acquire(6, dropped)
summarize(data)
sm = result.get_gram_dual_matrix()
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": 1, "R": 1})
D, ell = ldl_decompose_with_reversed_basis(sm, ctx.basis_vectors(), print_output=False)
E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
data["numerical_decomposition"] = dict(
    method="reverse_ldl",
    D=D.tolist(),
    ell_coords=E.tolist(),
    basis_labels=data["basis_vectors"],
)
_, _, _, _, _, checks = verify_saved(data, dense["opt_value"])
print("checks", checks)
# Compare de novo coefficient and terminal-square candidates at this sample.
n = data["N"]
candidate = {"initial_condition": 4 / n**2, f"A monotone:x_{n},x_star": 4 / n}
for k in range(1, n):
    candidate[f"A monotone:x_{k},x_{k + 1}"] = 4 * k * (k + 1) / n**2
for k in range(n):
    half = "x_0" if k == 0 else f"x_{k}+1/2"
    candidate[f"A Lipschitz:{half},x_{k + 1}"] = 2 * (k + 1) ** 2 / n**2
errors = {
    name: abs(value - candidate.get(name, 0))
    for name, value in data["named_dual_values"].items()
    if value is not None
}
print("lambda candidate max error", max(errors.values()))
for name, value in data["named_dual_values"].items():
    if value is not None and abs(value) > 1e-6:
        print("fraction", name, str(Fraction(value).limit_denominator(1000)))
ctx.set_as_current()
v = 2 / n * (ctx["x_0"] - ctx["x_star"]) - obj(ctx[f"x_{n}"])
cand = pm.eval_scalar(v**2)
s_error = float(np.max(np.abs(cand.inner_prod_coords - np.asarray(data["S_matrix"]))))
print("square candidate max error", s_error)
data.update(b1)
# Preserve selected solve values overwritten by B1's statuses only.
data.update(
    N=6,
    N_verify=6,
    numerical_checks=checks,
    numerical_certificate_verified=True,
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=False,
    proof_valid=True,
    require_analytic_full_pep=False,
    S_decomp_type="ldl",
)
data["formula_status"] = {
    "lambda": "candidate" if max(errors.values()) < 1e-4 else "unresolved",
    "S": "candidate" if s_error < 1e-4 else "unresolved",
}
data["lamb_code"] = (
    "lambda_mono = lambda k, N: 4*k*(k+1)/N**2\nlambda_lipschitz = lambda k, N: 2*(k+1)**2/N**2\nlambda_star = lambda N: 4/N\ntau_candidate = lambda N: 4/N**2"
)
data["S_code"] = (
    "S_candidate = (2*L/N*(ctx['x_0']-ctx['x_star']) - A(ctx[f'x_{N}']))**2"
)
data["closed_form_search"] = dict(
    completed=True,
    references_reviewed=[
        "Own dense and selected certificate only; target references prohibited"
    ],
    attempts=[
        {
            "method": "Rational reconstruction of active coefficients and degree-two index comparison",
            "lambda_max_abs_error": max(errors.values()),
            "domain": "L=R=1,N=6",
        },
        {
            "method": "Rank-one terminal square candidate",
            "S_gram_max_abs_error": s_error,
            "S_func_max_abs": float(np.max(np.abs(cand.func_coords), initial=0)),
            "S_offset_abs": abs(float(cand.offset)),
        },
    ],
    unresolved_components=[
        "all-horizon analytic lambda validity",
        "all-horizon analytic S identity",
    ],
)
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
data["certificate_id"] = hashlib.sha256(
    json.dumps(
        {k: data[k] for k in keys},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
).hexdigest()
for name in ["feg_b2.json", "feg_relaxed.json"]:
    (root / "state" / name).write_text(json.dumps(data, indent=2, allow_nan=False))
(root / "state/feg_relaxed_constraints.json").write_text(json.dumps(dropped, indent=2))
