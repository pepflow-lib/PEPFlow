# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Adopt a consistent basis and verify every expression component."""

import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT
sys.path.insert(0, str(ROOT / "supplementary"))
from certificate_capture import (  # noqa: E402, F401 -- Required by exec of dual_feg_b3.json#certificate_check_code. Paths initialized above.
    get_pep_setup,
)

# Preserve the recorded import initialization order.
# isort: split
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
from group_b3 import (  # noqa: E402 - imports follow runtime or notebook setup
    group,
    recheck,
)

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup
from pepflow.lyapunov_utils import (  # noqa: E402 - imports follow runtime or notebook setup
    find_symmetric_coefficient_matrix,
)

certificate = json.loads((ROOT / "state/dual_feg_b3.json").read_text())
for field in ["certificate_check_code", "decomposition_code", "grouping_code"]:
    exec(compile(certificate[field], field, "exec"), globals())
ctx.set_as_current()
params_sp = {"L": sp.Integer(1), "R": sp.Integer(1)}
N_int = certificate["N_verify"]


def V_k_basis(k):
    if k == 0:
        return []
    if k == N_int:
        return [obj(ctx[f"x_{N_int}"]), ctx["x_0"] - ctx[f"x_{N_int}"]]
    return [
        obj(ctx[f"x_{N_int}"]),
        ctx[f"z_{k}"],
        ctx[f"x_{k}"] - ctx[f"x_{N_int}"],
        ctx["x_0"] - ctx[f"x_{N_int}"],
    ]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == N_int:
        return ["A_N", "x_0-x_N"]
    return ["A_N", f"z_{k}", f"x_{k}-x_N", "x_0-x_N"]


def coeff_pattern(k, N):
    if k == 0:
        return np.zeros((0, 0))
    if k == N:
        return np.array([[2, -2 / N], [-2 / N, 0]])
    t = N - k
    return np.array(
        [
            [0, -2, 2 / t, -2 / N],
            [-2, -2, 2 / t, 0],
            [2 / t, 2 / t, 0, 0],
            [-2 / N, 0, 0, 0],
        ]
    )


def V_k_structure(k):
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    return sum(
        (float(C[i, j]) * vectors[i] * vectors[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )


coeff_by_k = {}
residuals = {}
component_residuals = {}
pattern_errors = {}
for k in range(N_int + 1):
    vectors = V_k_basis(k)
    M = np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords, dtype=float)
    if vectors:
        B = np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
        assert (
            np.linalg.matrix_rank(B, tol=1e-7)
            == len(vectors)
            == certificate["rank_profile"][k]
        )
    else:
        B = np.zeros((len(ctx.basis_vectors()), 0))
        assert np.linalg.matrix_rank(M, tol=1e-4) == 0
    C = find_symmetric_coefficient_matrix(
        lyap[k],
        vectors,
        pep_context=ctx,
        resolve_parameters={n: v for n, v in params_sp.items()},
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    coeff_by_k[k] = C
    err = float(np.linalg.norm(B @ C @ B.T - M, ord="fro"))
    assert err <= 1e-5 * max(1.0, np.linalg.norm(M, ord="fro"))
    residuals[k] = err
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    component_residuals[k] = {
        "gram": float(np.max(np.abs(diff.inner_prod_coords), initial=0)),
        "function": float(np.max(np.abs(diff.func_coords), initial=0)),
        "offset": abs(float(diff.offset)),
    }
    assert max(component_residuals[k].values()) <= 1e-4 + 1e-5 * float(
        np.max(np.abs(M), initial=0)
    )
    target = pm.eval_scalar(lyap[k])
    assert np.max(np.abs(target.func_coords), initial=0) == 0 and target.offset == 0
    pattern_errors[k] = float(np.max(np.abs(C - coeff_pattern(k, N_int)), initial=0))
    assert pattern_errors[k] <= 1e-4
    print(
        k,
        V_k_basis_labels(k),
        "residual",
        err,
        "pattern error",
        pattern_errors[k],
        flush=True,
    )
other = json.loads((ROOT / "supplementary/certificate_N8.json").read_text())
obs8 = group(other)
ctx8, pb8, obj8, pm8, _, _, _ = recheck(other)
ctx8.set_as_current()
errors8 = {}
for k in range(9):
    vs = (
        []
        if k == 0
        else (
            [obj8(ctx8["x_8"]), ctx8["x_0"] - ctx8["x_8"]]
            if k == 8
            else [
                obj8(ctx8["x_8"]),
                ctx8[f"z_{k}"],
                ctx8[f"x_{k}"] - ctx8["x_8"],
                ctx8["x_0"] - ctx8["x_8"],
            ]
        )
    )
    B = (
        np.column_stack([pm8.eval_vector(v).coords for v in vs]).astype(float)
        if vs
        else np.zeros((len(ctx8.basis_vectors()), 0))
    )
    M = np.asarray(obs8["lyap_inner_prod_coords"][k])
    errors8[k] = float(np.max(np.abs(B @ coeff_pattern(k, 8) @ B.T - M), initial=0))
    assert errors8[k] <= 1e-4
print("N8 formula expression errors", errors8)
ctx.set_as_current()
basis_code = inspect.getsource(V_k_basis) + "\n" + inspect.getsource(V_k_basis_labels)
coeff_code = inspect.getsource(coeff_pattern)
structure_code = inspect.getsource(V_k_structure)
state = {
    **certificate,
    "basis_templates": {
        "interior": ["A_N", "z_k", "x_k-x_N", "x_0-x_N"],
        "initial": [],
        "terminal": ["A_N", "x_0-x_N"],
    },
    "basis_code": basis_code,
    "structure_code": structure_code,
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": coeff_code,
    "coefficient_formula_status": "candidate",
    "expression_structure": {
        "quadratic_convention": "sum_ij C_ij <v_i,v_j>, symmetric C; off-diagonal entries count twice",
        "interior": {
            "index_domain": "1 <= k <= N-1",
            "basis_labels": ["A_N", "z_k", "x_k-x_N", "x_0-x_N"],
            "coefficients": "C_01=-2, C_11=-2, C_02=C_12=2/(N-k), C_03=-2/N, symmetric; all remaining independent entries zero (normalized L=1 candidate)",
        },
        "initial": {"index_domain": "k=0", "basis_labels": [], "coefficients": "V_0=0"},
        "terminal": {
            "index_domain": "k=N",
            "basis_labels": ["A_N", "x_0-x_N"],
            "coefficients": "C_00=2, C_01=-2/N, C_11=0 (normalized L=1 candidate)",
        },
        "function_terms": [],
        "constant_terms": [],
    },
    "unresolved_coefficients": [],
    "numerical_reconstruction": {
        "certificate_id": certificate["certificate_id"],
        "required_indices": list(range(N_int + 1)),
        "quadratic_residuals": residuals,
        "component_residuals": component_residuals,
        "tolerances": {
            "indep_tol": 1e-7,
            "span_tol": 1e-5,
            "component_atol": 1e-4,
            "component_rtol": 1e-5,
        },
        "passed": True,
    },
    "coefficient_candidate_checks": {
        "selected_coefficient_errors": pattern_errors,
        "N8_expression_errors": errors8,
    },
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(ROOT / "state/dual_feg_b4.json").write_text(json.dumps(state, indent=2))
