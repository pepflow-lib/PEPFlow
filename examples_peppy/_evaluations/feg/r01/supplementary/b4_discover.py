"""Candidate search and complete basis reconstruction for saved B3 sums."""

import json
import runpy
import sys
from pathlib import Path

import numpy as np

import pepflow as pf
from pepflow.lyapunov_utils import (
    find_basis_with_sparsest_coefficients,
    find_symmetric_coefficient_matrix,
    vectors_in_column_space,
)

root = Path.cwd()
b3 = json.loads((root / "state/feg_b3.json").read_text())
sys.argv = ["supplementary/b3_probe.py", "state/feg_b3.json"]
scope = runpy.run_path(str(root / "supplementary/b3_probe.py"))
ctx, pb, obj, pm, lyap = (scope[key] for key in ("ctx", "pb", "obj", "pm", "lyap"))
N_int, params_sp, ranks = (scope[key] for key in ("N_int", "params_sp", "ranks"))
assert scope["certificate_checked"] and scope["grouping_checked"]
assert ranks == b3["rank_profile"]
evidence = json.loads((root / b3["rank_search"]["evidence_path"]).read_text())
assert (
    evidence["summary"] == b3["rank_search"]
    and evidence["summary"]["status"] == "confirmed"
)
for k, v in enumerate(lyap):
    ev = pm.eval_scalar(v)
    assert np.allclose(
        ev.inner_prod_coords, b3["lyap_inner_prod_coords"][k], atol=1e-4, rtol=1e-5
    )
    assert np.allclose(ev.func_coords, b3["lyap_func_coords"][k], atol=1e-4, rtol=1e-5)
    assert abs(ev.offset - b3["lyap_offsets"][k]) <= 1e-4

# BEGIN CANDIDATES
candidate_pairs = []
for k in range(1, N_int + 1):
    candidate_pairs.extend(
        [(f"g_{k}", obj(ctx[f"x_{k}"])), (f"x_{k}-x_0", ctx[f"x_{k}"] - ctx["x_0"])]
    )
base = [(str(v), v) for v in ctx.basis_vectors()]
base += [(f"x_{k}", ctx[f"x_{k}"]) for k in range(N_int + 1)]
base += [(f"x_{2 * k + 1}/2", ctx[f"x_{2 * k + 1}/2"]) for k in range(1, N_int)]
candidate_pairs.extend(base)
for i, (label_i, vi) in enumerate(base):
    for label_j, vj in base[i + 1 :]:
        candidate_pairs.append((f"({label_i})-({label_j})", vi - vj))
unique_pairs, unique_coords = [], []
for label, v in candidate_pairs:
    coords = np.asarray(pm.eval_vector(v).coords, float)
    if np.linalg.norm(coords) <= 1e-12:
        continue
    if any(np.allclose(coords, old, atol=1e-12, rtol=0) for old in unique_coords):
        continue
    unique_pairs.append((label, v))
    unique_coords.append(coords)
candidates = [v for _, v in unique_pairs]
label_by_id = {id(v): label for label, v in unique_pairs}
print("Unique nonzero candidates:", len(candidates))
in_column = {}
for k in range(1, N_int + 1):
    in_column[k] = vectors_in_column_space(
        lyap[k],
        candidates,
        pep_context=ctx,
        resolve_parameters=params_sp,
        rtol=1e-4,
        atol=1e-4,
    )
    print(f"V_{k} column-space candidates:")
    for v in in_column[k]:
        print("   " + label_by_id[id(v)])
# END CANDIDATES

# BEGIN SEARCH
search_results = {}
for k in range(1, N_int + 1):
    sparse_basis, C_sparse = find_basis_with_sparsest_coefficients(
        lyap[k],
        in_column[k],
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=1e-6,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    assert len(sparse_basis) == ranks[k]
    chosen_labels = [label_by_id[id(v)] for v in sparse_basis]
    search_results[k] = {"labels": chosen_labels, "matrix": C_sparse.tolist()}
    print(f"k={k}, rank={ranks[k]} sparse basis: {chosen_labels}")
    print(f"zero coefficients: {np.sum(np.abs(C_sparse) < 1e-6)}/{C_sparse.size}")
# END SEARCH


# BEGIN BASIS
def V_k_basis(k):
    return [] if k == 0 else [obj(ctx[f"x_{k}"]), ctx[f"x_{k}"] - ctx["x_0"]]


def V_k_basis_labels(k):
    return [] if k == 0 else [f"A(x_{k})", f"x_{k}-x_0"]


for k in range(N_int + 1):
    vecs = V_k_basis(k)
    independent_rank = (
        int(
            np.linalg.matrix_rank(
                np.column_stack([pm.eval_vector(v).coords for v in vecs]).astype(float),
                tol=1e-7,
            )
        )
        if vecs
        else 0
    )
    assert independent_rank == len(vecs) == ranks[k]
    print(f"k={k}: rank {independent_rank} basis {V_k_basis_labels(k)}")
# END BASIS

# BEGIN COEFFICIENTS
coeff_by_k, coefficient_residuals = {}, {}
for k in range(N_int + 1):
    vecs = V_k_basis(k)
    C = find_symmetric_coefficient_matrix(
        lyap[k],
        vecs,
        pep_context=ctx,
        resolve_parameters=params_sp,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    target = np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords, float)
    matrix = (
        np.column_stack([pm.eval_vector(v).coords for v in vecs]).astype(float)
        if vecs
        else np.zeros((len(ctx.basis_vectors()), 0))
    )
    residual = float(np.linalg.norm(matrix @ C @ matrix.T - target, ord="fro"))
    assert residual <= 1e-5 * max(1.0, np.linalg.norm(target, ord="fro"))
    coeff_by_k[k], coefficient_residuals[k] = C, residual
    print(f"k={k}: coefficient reconstruction residual {residual:.3g}")
    if vecs:
        pf.pprint_labeled_matrix(
            C, V_k_basis_labels(k), V_k_basis_labels(k), precision=8
        )
    else:
        print("Empty quadratic basis, C shape", C.shape)
    nonquadratic = pm.eval_scalar(lyap[k])
    assert np.max(np.abs(nonquadratic.func_coords), initial=0) <= 1e-5
    assert abs(nonquadratic.offset) <= 1e-5
    print(
        "Function coordinates:",
        nonquadratic.func_coords,
        "offset:",
        nonquadratic.offset,
    )
# END COEFFICIENTS


# BEGIN STRUCTURE
def V_k_structure(k):
    vecs = V_k_basis(k)
    C = coeff_by_k[k]
    return sum(
        (float(C[i, j]) * vecs[i] * vecs[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )


component_residuals = {}
for k in range(N_int + 1):
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for name, residual, reference in (
        ("gram", diff.inner_prod_coords, target.inner_prod_coords),
        ("function", diff.func_coords, target.func_coords),
        ("offset", diff.offset, target.offset),
    ):
        error = float(np.max(np.abs(np.asarray(residual, float)), initial=0))
        scale = float(np.max(np.abs(np.asarray(reference, float)), initial=0))
        assert error <= 1e-4 + 1e-5 * scale
        component_residuals[str(k)][name] = error
print("Complete expression reconstruction:", component_residuals)
# END STRUCTURE

source = Path(__file__).read_text()


def block(label):
    return source.split(f"# BEGIN {label}\n")[1].split(f"# END {label}")[0]


unknowns = [
    {
        "name": f"c_{i}{j}",
        "arguments": ["k", "N", "L"],
        "role": f"C[{i},{j}]" + (f" = C[{j},{i}]" if i != j else ""),
        "index_domain": "1 <= k <= N",
    }
    for i, j in ((0, 0), (0, 1), (1, 1))
]
structure = {
    "quadratic_convention": "V = sum_ij C_ij <v_i,v_j>; symmetric C; off-diagonals counted twice",
    "interior": {
        "index_domain": "1 <= k <= N-1 (a=b=1)",
        "basis_labels": ["A(x_k)", "x_k-x_0"],
        "coefficients": {"00": "c_00(k,N,L)", "01": "c_01(k,N,L)", "11": "c_11(k,N,L)"},
    },
    "initial": {
        "index_domain": "k=0",
        "basis_labels": [],
        "coefficients": {},
        "value": "0",
    },
    "terminal": {
        "index_domain": "k=N",
        "basis_labels": ["A(x_N)", "x_N-x_0"],
        "coefficients": {"00": "c_00(N,N,L)", "01": "c_01(N,N,L)", "11": "c_11(N,N,L)"},
    },
    "function_terms": [],
    "constant_terms": [],
}
state = {
    **b3,
    "basis_templates": ["A(x_k)", "x_k-x_0"],
    "basis_code": block("BASIS"),
    "structure_code": block("STRUCTURE"),
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": None,
    "coefficient_formula_status": "unresolved",
    "expression_structure": structure,
    "unresolved_coefficients": unknowns,
    "basis_search": search_results,
    "numerical_reconstruction": {
        "certificate_id": b3["certificate_id"],
        "required_indices": list(range(N_int + 1)),
        "quadratic_residuals": coefficient_residuals,
        "component_residuals": component_residuals,
        "tolerances": {
            "indep_tol": 1e-7,
            "span_tol": 1e-5,
            "component_atol": 1e-4,
            "component_rtol": 1e-5,
        },
        "passed": True,
    },
}
(root / "state/feg_b4.json").write_text(json.dumps(state, indent=2, allow_nan=False))
print("B4 reconstruction complete")
