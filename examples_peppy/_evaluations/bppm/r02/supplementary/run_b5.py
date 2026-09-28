# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np
import sympy as sp
from bppm_setup import get_pep_setup

# local helper resolved by the notebook runtime path
from runtime import ATTEMPT  # ty: ignore[unresolved-import]

# Preserve the recorded import initialization order.
# isort: split
from bppm_setup import (  # noqa: F401 -- Required by exec of bppm_b4.json#certificate_check_code.
    f,
    h,
)

# Preserve the recorded import initialization order.
# isort: split
from numbers import (  # noqa: F401 -- Required by exec of bppm_b4.json#certificate_check_code.
    Number,
)

import pepflow as pf

notebook_dir = ATTEMPT
b4 = json.loads((ATTEMPT / "state/bppm_b4.json").read_text())
certificate = b4
N_int = b4["N_verify"]
ctx, pb, obj = get_pep_setup(N_int, {})
pb.set_relaxed_constraints(b4["relaxed_constraints"])
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(compile(b4[field], f"<B3-{field}>", "exec"), globals())
coeff_by_k = {
    int(k): np.asarray(v).reshape((0, 0) if int(k) == 0 else (4, 4))
    for k, v in b4["coeff_by_k"].items()
}
exec(compile(b4["basis_code"], "<B4-basis>", "exec"), globals())
exec(compile(b4["structure_code"], "<B4-structure>", "exec"), globals())
pm = pf.ExpressionManager(
    ctx, resolve_parameters={"alpha": sp.Integer(1), "R": sp.Integer(1)}
)
component_residuals = {}
for k in range(N_int + 1):
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    row = {
        "gram": max_abs(diff.inner_prod_coords),
        "function": max_abs(diff.func_coords),
        "offset": max_abs(diff.offset),
    }
    assert max(row.values()) <= 1e-4
    component_residuals[k] = row
cells = json.loads((ATTEMPT / "supplementary/b5_cells.json").read_text())
for i, cell in enumerate(cells):
    if cell["kind"] == "code":
        exec(compile(cell["source"], f"<B5-cell-{i}>", "exec"), globals())
state = {
    **b4,
    "proof_checks": proof_checks,
    "proof_residuals": proof_residuals,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": all(proof_checks.values()),
    "coefficient_formula_status": "verified",
    "lyapunov_formula": "V_k = k/N*(f(x_k)-f(x_star)) + (D_h(x_star,x_k)-D_h(x_star,x_0))/(alpha*N), 0<=k<=N",
    "unshifted_lyapunov_formula": "Phi_k = k/N*(f(x_k)-f(x_star)) + D_h(x_star,x_k)/(alpha*N)",
    "theorem": "0 <= f(x_N)-f(x_star) <= R/(alpha*N), for alpha>0, R>=0, integer N>=1",
    "proof_arguments": {
        "step": "Exact symbolic one-step PEPFlow identity with all four convex interpolation families; no square remainder.",
        "base": "Separate initial context: V0=0 and first-step identity, including N=1.",
        "boundary": "metric - R/(alpha*N) = V_N + initial_residual/(alpha*N) + C_h(star,N)/(alpha*N).",
        "signs": "All local multipliers nonnegative for 1<=j<=N, alpha>0, N>=1; convex residuals nonpositive; terminal C_h=-D_h nonpositive.",
        "domain": "Real finite-dimensional space, supplied convex/differentiability assumptions, exact well-defined proximal steps; alpha>0, R>=0, integer N>=1. No division by R or N-1.",
        "normalization": "D_h(x_star,x_0)<=R, not R squared; positive alpha*N. Phi0<=R/(alpha*N), metric<=PhiN<=Phi0.",
    },
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": b4["expression_structure"],
    "remaining_unknowns": [],
    "local_multiplier_code": "def local_weights(j,N,alpha):\n    return [1/N,(j-1)/N,j/(alpha*N),(j-1)/(alpha*N)]\n",
    "symbolic_source_cells": "supplementary/b5_cells.json",
    "require_analytic_full_pep": False,
    "global_formula_status": "Separate analytic full-PEP formula flag remains unverified; completed local Lyapunov proof establishes the theorem.",
}
(ATTEMPT / "state/bppm_b5.json").write_text(json.dumps(state, indent=2))
print("Exact B5 proof state saved; final notebook delivery checks still pending.")
