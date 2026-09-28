# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# CELL
from pepflow.lyapunov_utils import (
    find_basis_with_sparsest_coefficients,
    find_symmetric_coefficient_matrix,
    vectors_in_column_space,
)

b3 = json.loads((notebook_dir / "state/pgm_b3.json").read_text())
assert certificate_checked and grouping_checked
assert b3["certificate_id"] == certificate["certificate_id"]
assert b3["rank_search"]["status"] == "confirmed"
assert b3["rank_search"]["boundary_exclusions"] == {"left": 1, "right": 1}
assert ranks == b3["rank_profile"]
for k, Vk in enumerate(lyap):
    evaluated = pm.eval_scalar(Vk)
    for actual, saved in (
        (evaluated.inner_prod_coords, b3["lyap_inner_prod_coords"][k]),
        (evaluated.func_coords, b3["lyap_func_coords"][k]),
        (evaluated.offset, b3["lyap_offsets"][k]),
    ):
        assert np.allclose(
            np.asarray(actual, dtype=float),
            np.asarray(saved, dtype=float),
            atol=1e-4,
            rtol=1e-5,
        )
print("Selected N=4 partial sums match the B3 handoff; interior 1 <= k <= N-1.")

# CELL
candidate_pairs = []
for k in range(N_int + 1):
    candidate_pairs.append((f"d_{k}", ctx[f"x_{k}"] - ctx["x_star"]))
    candidate_pairs.append((f"grad_f_{k}", f.grad(ctx[f"x_{k}"])))
    if k:
        candidate_pairs.append((f"s_g_{k}", g.grad(ctx[f"x_{k}"])))
candidate_pairs.append(("grad_f_star", f.grad(ctx["x_star"])))
unique_pairs = []
seen_coords = []
for label, vector in candidate_pairs:
    coordinates = np.asarray(pm.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(coordinates) < 1e-7:
        continue
    if any(np.allclose(coordinates, old, atol=1e-10, rtol=0) for old in seen_coords):
        continue
    unique_pairs.append((label, vector))
    seen_coords.append(coordinates)
labels_by_id = {id(vector): label for label, vector in unique_pairs}

# CELL
spanning_by_k = {}
for k in range(1, N_int + 1):
    in_col = vectors_in_column_space(
        lyap[k],
        [v for _, v in unique_pairs],
        pep_context=ctx,
        resolve_parameters=params_sp,
        rtol=1e-4,
        atol=1e-4,
    )
    spanning_by_k[k] = in_col
    print(f"V_{k} column-space candidates:")
    for vector in in_col:
        print("   " + labels_by_id[id(vector)])

# CELL
sparse_bases = {}
sparse_coefficients = {}
for k in range(1, N_int + 1):
    sparse, C = find_basis_with_sparsest_coefficients(
        lyap[k],
        spanning_by_k[k],
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=1e-6,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    assert len(sparse) == ranks[k]
    sparse_bases[k] = sparse
    sparse_coefficients[k] = C
    print(f"k={k}, rank={ranks[k]}")
    print("  sparse basis:", [labels_by_id[id(v)] for v in sparse])
    print(f"  zero coefficients: {int(np.sum(np.abs(C) < 1e-6))}/{C.size}")


# CELL
def V_k_basis(k):
    if k == 0:
        return []
    if k == N_int:
        return [ctx["x_0"] - ctx["x_star"]]
    return [
        ctx["x_0"] - ctx["x_star"],
        f.grad(ctx[f"x_{k}"]),
        ctx[f"x_{k + 1}"] - ctx["x_star"],
        g.grad(ctx[f"x_{k + 1}"]),
        f.grad(ctx["x_star"]),
    ]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == N_int:
        return ["d_0"]
    return ["d_0", f"grad_f_{k}", f"d_{k + 1}", f"s_g_{k + 1}", "grad_f_star"]


for k in range(N_int + 1):
    vectors = V_k_basis(k)
    coordinates = (
        np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
        if vectors
        else np.zeros((len(ctx.basis_vectors()), 0))
    )
    independent = int(np.linalg.matrix_rank(coordinates, tol=1e-7)) if vectors else 0
    assert independent == len(vectors) == ranks[k]
    print(f"k={k}: rank {independent} basis {V_k_basis_labels(k)}")

# CELL
coeff_by_k = {}
coefficient_residuals = {}
function_weights = {}
required_indices = list(range(N_int + 1))
for k in required_indices:
    vectors = V_k_basis(k)
    target = pm.eval_scalar(lyap[k])
    target_matrix = np.asarray(target.inner_prod_coords, dtype=float)
    if vectors:
        C = find_symmetric_coefficient_matrix(
            lyap[k],
            vectors,
            pep_context=ctx,
            resolve_parameters=params_sp,
            indep_tol=1e-7,
            span_tol=1e-5,
        )
        coordinates = np.column_stack(
            [pm.eval_vector(v).coords for v in vectors]
        ).astype(float)
        residual = float(
            np.linalg.norm(coordinates @ C @ coordinates.T - target_matrix, ord="fro")
        )
    else:
        C = np.zeros((0, 0))
        residual = float(np.linalg.norm(target_matrix, ord="fro"))
    assert residual <= 1e-5 * max(1.0, float(np.linalg.norm(target_matrix, ord="fro")))
    assert np.array_equal(C, C.T)
    coeff_by_k[k] = C
    coefficient_residuals[k] = residual
    print(f"k={k}: quadratic reconstruction residual {residual:.3e}")
    if vectors:
        pf.pprint_labeled_matrix(
            pf.MatrixWithNames(C, V_k_basis_labels(k), V_k_basis_labels(k))
        )
    if k:
        f_gap = f(ctx[f"x_{k}"]) - f(ctx["x_star"])
        g_gap = g(ctx[f"x_{k}"]) - g(ctx["x_star"])
        F = np.column_stack(
            [pm.eval_scalar(f_gap).func_coords, pm.eval_scalar(g_gap).func_coords]
        ).astype(float)
        weights = np.linalg.lstsq(
            F, np.asarray(target.func_coords, dtype=float), rcond=None
        )[0]
        assert (
            np.max(
                np.abs(F @ weights - np.asarray(target.func_coords, dtype=float)),
                initial=0,
            )
            < 1e-5
        )
    else:
        weights = np.zeros(2)
    function_weights[k] = weights.tolist()
    print(
        "Function terms: f gap weight, g gap weight =",
        weights,
        "offset =",
        float(target.offset),
    )
    assert abs(float(target.offset)) < 1e-5


# CELL
def V_k_structure(k):
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    value = sum(
        (float(C[i, j]) * vectors[i] * vectors[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )
    if k:
        af, ag = function_weights[k]
        value += af * (f(ctx[f"x_{k}"]) - f(ctx["x_star"]))
        value += ag * (g(ctx[f"x_{k}"]) - g(ctx["x_star"]))
    return value


component_residuals = {}
for k in required_indices:
    checked = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for name, values, scale_values in (
        ("gram", checked.inner_prod_coords, target.inner_prod_coords),
        ("function", checked.func_coords, target.func_coords),
        ("offset", checked.offset, target.offset),
    ):
        error = float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0))
        scale = float(np.max(np.abs(np.asarray(scale_values, dtype=float)), initial=0))
        assert error <= 1e-4 + 1e-5 * scale
        component_residuals[str(k)][name] = error
    print("Full expression residuals", k, component_residuals[str(k)])
print(
    "All indices reconstructed. Quadratic coefficients remain named unknown functions c_ij(k,N,L)."
)
