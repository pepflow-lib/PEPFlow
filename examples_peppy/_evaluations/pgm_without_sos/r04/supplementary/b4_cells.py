# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from itertools import combinations

from pgm_setup import f as setup_f
from pgm_setup import g as setup_g

from pepflow.lyapunov_utils import (
    find_basis_with_sparsest_coefficients,
    find_symmetric_coefficient_matrix,
    vectors_in_column_space,
)

b3 = json.loads((notebook_dir / "state/pgm_b3.json").read_text())
assert b3["certificate_id"] == certificate["certificate_id"]
assert ranks == b3["rank_profile"]
rank_evidence = json.loads(
    (notebook_dir / b3["rank_search"]["evidence_path"]).read_text()
)
assert rank_evidence["summary"] == b3["rank_search"]
assert b3["rank_search"]["boundary_exclusions"] == {"left": 1, "right": 1}
for k, value in enumerate(lyap):
    evaluated = pm.eval_scalar(value)
    assert np.allclose(
        evaluated.inner_prod_coords,
        b3["lyap_inner_prod_coords"][k],
        atol=1e-4,
        rtol=1e-5,
    )
    assert np.allclose(
        np.asarray(evaluated.func_coords, float),
        b3["lyap_func_coords"][k],
        atol=1e-4,
        rtol=1e-5,
    )
    assert abs(float(evaluated.offset) - b3["lyap_offsets"][k]) <= 1e-4
print(
    "Selected ranks:", ranks, "; interior 1 <= k <= N-1; endpoints checked separately."
)
# CELL
candidate_pairs = [
    ("e_0", ctx["x_0"] - ctx["x_star"]),
    ("s_star", setup_f.grad(ctx["x_star"])),
]
for j in range(1, N_int + 1):
    candidate_pairs += [
        (f"e_{j}", ctx[f"x_{j}"] - ctx["x_star"]),
        (f"p_{j}", setup_f.grad(ctx[f"x_{j}"]) - setup_f.grad(ctx["x_star"])),
    ]
candidate_pairs += [(str(v), v) for v in ctx.basis_vectors()]
candidate_pairs += [(f"x_{j}", ctx[f"x_{j}"]) for j in range(N_int + 1)]
base_pairs = list(candidate_pairs)
for (label1, v1), (label2, v2) in combinations(base_pairs, 2):
    candidate_pairs.append((f"({label1})-({label2})", v1 - v2))
unique_pairs = []
coordinate_keys = set()
for label, vector in candidate_pairs:
    coords = np.asarray(pm.eval_vector(vector).coords, float)
    if np.linalg.norm(coords) <= 1e-12:
        continue
    key = tuple(np.round(coords, 12))
    if key not in coordinate_keys:
        unique_pairs.append((label, vector))
        coordinate_keys.add(key)
print("Distinct nonzero candidates:", len(unique_pairs))
# CELL
in_column = {}
for k in range(1, N_int + 1):
    in_column[k] = vectors_in_column_space(
        lyap[k],
        [v for _, v in unique_pairs],
        pep_context=ctx,
        resolve_parameters=params_sp,
        rtol=1e-4,
        atol=1e-4,
    )
    print(f"V_{k} column-space candidates:")
    for label, vector in unique_pairs:
        if any(vector is selected for selected in in_column[k]):
            print("   ", label)
# CELL
sparse_bases = {}
sparse_coeffs = {}
for k in range(1, N_int + 1):
    sparse_basis, sparse_C = find_basis_with_sparsest_coefficients(
        lyap[k],
        in_column[k],
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=1e-6,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    assert len(sparse_basis) == ranks[k]
    sparse_bases[k], sparse_coeffs[k] = sparse_basis, sparse_C
    labels = [
        next(label for label, v in unique_pairs if v is selected)
        for selected in sparse_basis
    ]
    print(f"k={k}: rank {ranks[k]}; sparse basis: {labels}")
    print(f"zero coefficients: {int(np.sum(np.abs(sparse_C) < 1e-6))}/{sparse_C.size}")


# CELL
# Adopt one uniform interpretable order even if a sparse search returns differences.
def V_k_basis(k):
    if k == 0:
        return []
    if k == N_int:
        return [ctx["x_0"] - ctx["x_star"]]
    return [
        ctx["x_0"] - ctx["x_star"],
        ctx[f"x_{k}"] - ctx["x_star"],
        setup_f.grad(ctx[f"x_{k}"]) - setup_f.grad(ctx["x_star"]),
        setup_f.grad(ctx["x_star"]),
    ]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == N_int:
        return ["e_0"]
    return ["e_0", f"e_{k}", f"p_{k}", "s_star"]


for k in range(N_int + 1):
    vectors = V_k_basis(k)
    coordinate_matrix = (
        np.column_stack([np.asarray(pm.eval_vector(v).coords, float) for v in vectors])
        if vectors
        else np.zeros((len(ctx.basis_vectors()), 0))
    )
    basis_rank = int(np.linalg.matrix_rank(coordinate_matrix, tol=1e-7))
    assert basis_rank == len(vectors) == ranks[k]
    print(f"k={k}: rank {basis_rank} basis {V_k_basis_labels(k)}")
# CELL
coeff_by_k = {}
coefficient_residuals = {}
function_sample_coefficients = {}
for k in range(N_int + 1):
    vectors = V_k_basis(k)
    target = pm.eval_scalar(lyap[k])
    matrix = np.asarray(target.inner_prod_coords, float)
    if not vectors:
        C = np.zeros((0, 0))
        reconstructed = np.zeros_like(matrix)
    else:
        C = find_symmetric_coefficient_matrix(
            lyap[k],
            vectors,
            pep_context=ctx,
            resolve_parameters=params_sp,
            indep_tol=1e-7,
            span_tol=1e-5,
        )
        B = np.column_stack(
            [np.asarray(pm.eval_vector(v).coords, float) for v in vectors]
        )
        reconstructed = B @ C @ B.T
    residual = float(np.linalg.norm(reconstructed - matrix, ord="fro"))
    assert residual <= 1e-5 * max(1.0, float(np.linalg.norm(matrix, ord="fro")))
    assert np.array_equal(C, C.T)
    coeff_by_k[k] = C
    coefficient_residuals[k] = residual
    print(f"k={k}: quadratic reconstruction residual {residual:.3e}")
    if vectors:
        pf.pprint_labeled_matrix(C, V_k_basis_labels(k), precision=7)
    if k == 0:
        function_sample_coefficients[k] = [0.0, 0.0]
        assert np.allclose(np.asarray(target.func_coords, float), 0, atol=1e-5, rtol=0)
    else:
        Fgap = setup_f(ctx[f"x_{k}"]) - setup_f(ctx["x_star"])
        Ggap = setup_g(ctx[f"x_{k}"]) - setup_g(ctx["x_star"])
        Fbasis = np.column_stack(
            [
                np.asarray(pm.eval_scalar(term).func_coords, float)
                for term in (Fgap, Ggap)
            ]
        )
        weights = np.linalg.lstsq(
            Fbasis, np.asarray(target.func_coords, float), rcond=None
        )[0]
        assert np.allclose(
            Fbasis @ weights, np.asarray(target.func_coords, float), atol=1e-5, rtol=0
        )
        function_sample_coefficients[k] = weights.tolist()
        print("Function coefficients [f_k-f_star,g_k-g_star]:", weights)
    assert abs(float(target.offset)) <= 1e-5
    print("Constant offset:", float(target.offset))


# CELL
# Full expression assembly: quadratic form plus identified function gaps.
def V_k_structure(k):
    if k == 0:
        return pf.Scalar.zero()
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    quadratic = sum(
        (float(C[i, j]) * vectors[i] * vectors[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )
    f_weight, g_weight = function_sample_coefficients[k]
    return (
        quadratic
        + f_weight * (setup_f(ctx[f"x_{k}"]) - setup_f(ctx["x_star"]))
        + g_weight * (setup_g(ctx[f"x_{k}"]) - setup_g(ctx["x_star"]))
    )


component_residuals = {}
for k in range(N_int + 1):
    residual = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[k] = {}
    for name, coords, target_coords in [
        ("gram", residual.inner_prod_coords, target.inner_prod_coords),
        ("function", residual.func_coords, target.func_coords),
        ("offset", residual.offset, target.offset),
    ]:
        error = float(np.max(np.abs(np.asarray(coords, float)), initial=0))
        scale = float(np.max(np.abs(np.asarray(target_coords, float)), initial=0))
        assert error <= 1e-4 + 1e-5 * scale
        component_residuals[k][name] = error
    print(f"k={k}: complete reconstruction", component_residuals[k])
print(
    "All indices reconstructed. Coefficient functions remain analytically unresolved."
)
