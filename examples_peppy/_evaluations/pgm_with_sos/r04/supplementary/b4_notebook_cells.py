# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from itertools import combinations

from pepflow.lyapunov_utils import (
    find_basis_with_sparsest_coefficients,
    find_symmetric_coefficient_matrix,
    vectors_in_column_space,
)

b3 = json.loads((notebook_dir / "state/pgm_b3.json").read_text())
certificate = b3
N_int = b3["N_verify"]
params_sp = json.loads(b3["params_json"])
# Replay the visible B3 construction and checks against this selected certificate.
selected_partial_sums = reconstruct_partial_sums(certificate)
assert selected_partial_sums["observation"]["certificate_id"] == b3["certificate_id"]
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
basis_vectors = ctx.basis_vectors()
basis_scalars = ctx.basis_scalars()
assert [str(v) for v in basis_vectors] == b3["basis_vectors"]
assert [str(v) for v in basis_scalars] == b3["basis_scalars"]
lyap = []
for k in range(N_int + 1):
    gram = np.array(selected_partial_sums["lyap_inner_prod_coords"][k])
    funcs = np.array(selected_partial_sums["lyap_func_coords"][k])
    offset = selected_partial_sums["lyap_offsets"][k]
    value = sum(
        (
            float(gram[i, j]) * basis_vectors[i] * basis_vectors[j]
            for i, j in np.ndindex(gram.shape)
        ),
        pf.Scalar.zero(),
    )
    value += (
        sum((float(c) * v for c, v in zip(funcs, basis_scalars)), pf.Scalar.zero())
        + offset
    )
    lyap.append(value)
    assert np.allclose(gram, b3["lyap_inner_prod_coords"][k], atol=1e-4, rtol=1e-5)
    assert np.allclose(funcs, b3["lyap_func_coords"][k], atol=1e-4, rtol=1e-5)
    assert abs(offset - b3["lyap_offsets"][k]) <= 1e-4
ranks = [
    int(
        np.linalg.matrix_rank(
            pm.eval_scalar(v).inner_prod_coords.astype(float), tol=1e-4
        )
    )
    for v in lyap
]
assert ranks == b3["rank_profile"]
assert b3["rank_search"]["boundary_exclusions"] == {"left": 1, "right": 1}
print(
    "Selected rank profile:",
    ranks,
    "confirmed horizons:",
    b3["rank_search"]["confirmed_horizons"],
)

# SECTION candidate_scan
candidate_pairs = [("x0-star", ctx["x_0"] - ctx["x_star"])]
for i in range(N_int + 1):
    candidate_pairs += [
        (f"x{i}-star", ctx[f"x_{i}"] - ctx["x_star"]),
        (f"a{i}-astar", f.grad(ctx[f"x_{i}"]) - f.grad(ctx["x_star"])),
    ]
    if i:
        candidate_pairs += [
            (f"hgrad{i}", f.grad(ctx[f"x_{i}"]) + g.grad(ctx[f"x_{i}"])),
            (f"proxstep{i}", ctx[f"x_{i - 1}"] - ctx[f"x_{i}"]),
        ]
candidate_pairs += [(str(v), v) for v in ctx.basis_vectors()]
base = list(candidate_pairs)
for (left, u), (right, v) in combinations(base, 2):
    candidate_pairs.append((f"({left})-({right})", u - v))
unique_pairs, seen_coords = [], []
for label, vector in candidate_pairs:
    coords = np.array(pm.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(coords) < 1e-7 or any(
        np.allclose(coords, previous, atol=1e-7, rtol=0) for previous in seen_coords
    ):
        continue
    unique_pairs.append((label, vector))
    seen_coords.append(coords)
labels_by_id = {id(vector): label for label, vector in unique_pairs}
in_column = {}
for k in range(1, N_int + 1):
    in_column[k] = vectors_in_column_space(
        lyap[k],
        [v for _, v in unique_pairs],
        pep_context=ctx,
        resolve_parameters=params_sp,
        atol=1e-4,
        rtol=1e-4,
    )
    print(f"V_{k} column-space candidates:")
    for vector in in_column[k]:
        print("  ", labels_by_id[id(vector)])

# SECTION basis_search
search_results = {}
for k in range(1, N_int + 1):
    searched_basis, searched_C = find_basis_with_sparsest_coefficients(
        lyap[k],
        in_column[k],
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=1e-6,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    assert len(searched_basis) == ranks[k]
    search_results[k] = {
        "labels": [labels_by_id[id(v)] for v in searched_basis],
        "C": searched_C.tolist(),
    }
    print(f"k={k}, rank={ranks[k]}")
    print("sparse basis:", search_results[k]["labels"])
    print(
        "zero coefficients:",
        int(np.sum(np.abs(searched_C) < 1e-6)),
        "/",
        searched_C.size,
    )


# SECTION basis_definition
def V_k_basis(k):
    if k == 0:
        return []
    if k == N_int:
        return [ctx["x_0"] - ctx["x_star"]]
    return [
        ctx["x_0"] - ctx["x_star"],
        ctx[f"x_{k}"] - ctx["x_star"],
        f.grad(ctx[f"x_{k}"]) - f.grad(ctx["x_star"]),
        f.grad(ctx[f"x_{k}"]),
    ]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == N_int:
        return ["x_0-x_star"]
    return ["x_0-x_star", f"x_{k}-x_star", f"a_{k}-a_star", f"a_{k}"]


for k in range(N_int + 1):
    vectors = V_k_basis(k)
    basis_rank = (
        int(
            np.linalg.matrix_rank(
                np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(
                    float
                ),
                tol=1e-7,
            )
        )
        if vectors
        else 0
    )
    assert basis_rank == len(vectors) == ranks[k]
    print(f"k={k}: rank {basis_rank} basis {V_k_basis_labels(k)}")

# SECTION coefficients
coeff_by_k, coefficient_residuals = {}, {}
for k in range(N_int + 1):
    vectors = V_k_basis(k)
    target = pm.eval_scalar(lyap[k]).inner_prod_coords.astype(float)
    if vectors:
        C = find_symmetric_coefficient_matrix(
            lyap[k],
            vectors,
            pep_context=ctx,
            resolve_parameters=params_sp,
            indep_tol=1e-7,
            span_tol=1e-5,
        )
        B = np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
        residual = float(np.linalg.norm(B @ C @ B.T - target, ord="fro"))
    else:
        C = np.zeros((0, 0))
        residual = float(np.linalg.norm(target, ord="fro"))
    assert np.array_equal(C, C.T)
    assert residual <= 1e-5 * max(1.0, np.linalg.norm(target, ord="fro"))
    coeff_by_k[k], coefficient_residuals[k] = C, residual
    print(f"k={k}: reconstruction residual {residual}")
    if vectors:
        pf.pprint_labeled_matrix(C, V_k_basis_labels(k))
    evaluated = pm.eval_scalar(lyap[k])
    print(
        "Function terms:",
        [
            (label, float(c))
            for label, c in zip(b3["basis_scalars"], evaluated.func_coords)
            if abs(float(c)) > 1e-6
        ],
        "offset:",
        evaluated.offset,
    )


# SECTION structure
def V_k_structure(k):
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    quadratic = sum(
        (float(C[i, j]) * vectors[i] * vectors[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )
    if k == 0:
        return quadratic
    f_weight = 1 if k == N_int else (k + 1) / (2 * N_int - k)
    g_weight = 1 if k == N_int else k / (2 * N_int - k)
    return (
        quadratic
        + f_weight * (f(ctx[f"x_{k}"]) - f(ctx["x_star"]))
        + g_weight * (g(ctx[f"x_{k}"]) - g(ctx["x_star"]))
    )


component_residuals = {}
for k in range(N_int + 1):
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    component_residuals[str(k)] = {
        "gram": maxabs(diff.inner_prod_coords),
        "function": maxabs(diff.func_coords),
        "offset": maxabs(diff.offset),
    }
    assert all(value <= 1e-4 for value in component_residuals[str(k)].values())
print("Full-component reconstruction:", component_residuals)


# Candidate coefficient formulas, inferred from the observed rational matrices.
def coeff_pattern(k, n, smoothness=1):
    ell = sp.sympify(smoothness)
    if k == 0:
        return sp.zeros(0)
    if k == n:
        return sp.Matrix([[-ell / (4 * n)]])
    C = sp.zeros(4)
    C[0, 0] = -ell / (4 * n)
    C[1, 1] = ell * (n - k) / (2 * n - k) ** 2
    C[2, 2] = 1 / (2 * ell * (2 * n - k))
    C[1, 3] = C[3, 1] = -sp.Rational(1, 2 * (2 * n - k))
    return C


for k in range(N_int + 1):
    predicted = np.array(coeff_pattern(k, N_int), dtype=float).reshape(
        coeff_by_k[k].shape
    )
    assert np.allclose(predicted, coeff_by_k[k], atol=1e-4, rtol=1e-5)
    print(f"k={k}: coefficient candidate residual {maxabs(predicted - coeff_by_k[k])}")
