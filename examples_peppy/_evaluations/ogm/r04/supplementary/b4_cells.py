# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# %%
from itertools import combinations

from pepflow.lyapunov_utils import (
    find_basis_with_sparsest_coefficients,
    find_symmetric_coefficient_matrix,
    vectors_in_column_space,
)

b3 = json.loads((notebook_dir / "state/ogm_b3.json").read_text())
assert b3["certificate_id"] == certificate["certificate_id"]
assert certificate_checked and grouping_checked
assert b3["rank_profile"] == ranks
assert b3["rank_search"]["status"] == "confirmed"
rank_evidence = json.loads(
    (notebook_dir / b3["rank_search"]["evidence_path"]).read_text()
)
assert rank_evidence["summary"] == b3["rank_search"]
assert b3["rank_search"]["boundary_exclusions"] == {"left": 1, "right": 1}
for k, Vk in enumerate(lyap):
    ev = pm.eval_scalar(Vk)
    for actual, saved in (
        (ev.inner_prod_coords, b3["lyap_inner_prod_coords"][k]),
        (ev.func_coords, b3["lyap_func_coords"][k]),
        (ev.offset, b3["lyap_offsets"][k]),
    ):
        assert np.allclose(
            np.asarray(actual, dtype=float),
            np.asarray(saved, dtype=float),
            atol=1e-4,
            rtol=1e-5,
        )
print("Selected N=4 replay matches B3; interior indices 1..3, endpoints 0 and 4.")
theta = theta_sequence(N_int)
candidate_pairs = [("d_0", ctx["x_0"] - ctx["x_star"])]
for k in range(1, N_int + 1):
    factor = theta[k] if k == N_int else 2 * theta[k]
    candidate_pairs.append(
        (
            f"q_{k}",
            ctx[f"z_{k}"] - ctx["x_star"] - factor / params_sp["L"] * ctx[f"g_{k}"],
        )
    )
for k in range(N_int + 1):
    for prefix in ("x", "z", "g"):
        candidate_pairs.append((f"{prefix}_{k}", ctx[f"{prefix}_{k}"]))
    if k:
        candidate_pairs.append((f"y_{k}", ctx[f"y_{k}"]))
candidate_pairs += [("x_star", ctx["x_star"])]
base = list(candidate_pairs)
for (la, va), (lb, vb) in combinations(base, 2):
    candidate_pairs.append((f"{la}-{lb}", va - vb))
unique_pairs, unique_coords = [], []
for label, vector in candidate_pairs:
    coords = np.asarray(pm.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(coords) <= 1e-6:
        continue
    if any(np.allclose(coords, old, atol=1e-6, rtol=0) for old in unique_coords):
        continue
    unique_pairs.append((label, vector))
    unique_coords.append(coords)
candidates = [v for label, v in unique_pairs]
labels_by_id = {id(v): label for label, v in unique_pairs}
print("Distinct nonzero candidates:", len(candidates))
# %%
spanning_by_k = {}
for k in range(1, N_int + 1):
    in_col = vectors_in_column_space(
        lyap[k],
        candidates,
        pep_context=ctx,
        resolve_parameters=params_sp,
        rtol=1e-4,
        atol=1e-4,
    )
    spanning_by_k[k] = in_col
    print(f"V_{k} column-space candidates:")
    for vector in in_col:
        print("  " + labels_by_id[id(vector)])
# %%
search_tolerances = dict(zero_tol=1e-6, indep_tol=1e-7, span_tol=1e-5)
search_basis, search_coeff = {}, {}
for k in range(1, N_int + 1):
    found, C = find_basis_with_sparsest_coefficients(
        lyap[k],
        spanning_by_k[k],
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=search_tolerances["zero_tol"],
        indep_tol=search_tolerances["indep_tol"],
        span_tol=search_tolerances["span_tol"],
    )
    assert len(found) == ranks[k]
    search_basis[k], search_coeff[k] = found, C
    print(f"k={k}: rank {ranks[k]}")
    print("  sparse basis:", [labels_by_id[id(v)] for v in found])
    print(f"  zero coefficients: {np.count_nonzero(np.abs(C) < 1e-6)}/{C.size}")


# %%
def V_k_basis(k):
    if k == 0:
        return []
    d = ctx["x_0"] - ctx["x_star"]
    factor = theta[k] if k == N_int else 2 * theta[k]
    qk = ctx[f"z_{k}"] - ctx["x_star"] - factor / params_sp["L"] * ctx[f"g_{k}"]
    return [d, qk] if k == N_int else [d, qk, ctx[f"g_{k}"]]


def V_k_basis_labels(k):
    return (
        []
        if k == 0
        else ["d_0", f"q_{k}"]
        if k == N_int
        else ["d_0", f"q_{k}", f"g_{k}"]
    )


for k in range(N_int + 1):
    vectors = V_k_basis(k)
    Q = (
        np.column_stack(
            [np.asarray(pm.eval_vector(v).coords, dtype=float) for v in vectors]
        )
        if vectors
        else np.zeros((len(ctx.basis_vectors()), 0))
    )
    rank = int(np.linalg.matrix_rank(Q, tol=1e-7)) if vectors else 0
    assert rank == len(vectors) == ranks[k]
    print(f"k={k}: rank {rank} basis {V_k_basis_labels(k)}")
# %%
coeff_by_k, coefficient_residuals = {}, {}
extraction_tolerances = dict(indep_tol=1e-7, span_tol=1e-5)
required_indices = list(range(N_int + 1))
function_coefficients = {}
for k in required_indices:
    vectors = V_k_basis(k)
    Q = (
        np.column_stack(
            [np.asarray(pm.eval_vector(v).coords, dtype=float) for v in vectors]
        )
        if vectors
        else np.zeros((len(ctx.basis_vectors()), 0))
    )
    C = (
        find_symmetric_coefficient_matrix(
            lyap[k],
            vectors,
            pep_context=ctx,
            resolve_parameters=params_sp,
            **extraction_tolerances,
        )
        if vectors
        else np.zeros((0, 0))
    )
    ev = pm.eval_scalar(lyap[k])
    target = np.asarray(ev.inner_prod_coords, dtype=float)
    assert np.array_equal(C, C.T)
    residual = float(np.linalg.norm(Q @ C @ Q.T - target, ord="fro"))
    assert residual <= 1e-5 * max(1.0, np.linalg.norm(target, ord="fro"))
    coeff_by_k[k], coefficient_residuals[k] = C, residual
    if k:
        fgap = obj(ctx[f"x_{k}"]) - obj(ctx["x_star"])
        fc = np.asarray(pm.eval_scalar(fgap).func_coords, dtype=float)
        function_coefficients[k] = float(
            np.asarray(ev.func_coords, dtype=float) @ fc / (fc @ fc)
        )
        assert np.allclose(
            function_coefficients[k] * fc,
            np.asarray(ev.func_coords, dtype=float),
            atol=1e-5,
            rtol=1e-5,
        )
    else:
        function_coefficients[k] = 0.0
        assert np.allclose(ev.func_coords, 0, atol=1e-5, rtol=0)
    assert abs(float(ev.offset)) <= 1e-5
    print(
        f"k={k}: quadratic residual {residual:.3g}; f(x_k)-f_star coefficient {function_coefficients[k]:.10g}; offset {ev.offset}"
    )
    if vectors:
        pf.pprint_labeled_matrix(C, V_k_basis_labels(k))
    pf.pprint_labeled_matrix(
        np.asarray(ev.func_coords, dtype=float).reshape(1, -1),
        ["function coefficients"],
        [str(v) for v in ctx.basis_scalars()],
    )


# %%
def coeff_pattern(k):
    tau = float(params_sp["L"]) / (2 * theta[N_int] ** 2)
    if k == 0:
        return np.zeros((0, 0))
    if k == N_int:
        return np.diag([-tau, tau])
    return np.diag(
        [-tau, tau, -(theta[k] ** 2) / (float(params_sp["L"]) * theta[N_int] ** 2)]
    )


formula_residuals = {}
for k, C in coeff_by_k.items():
    expected = coeff_pattern(k)
    error = float(np.max(np.abs(C - expected), initial=0))
    formula_residuals[k] = error
    assert error <= 1e-4
    expected_function = (
        0.0 if k == 0 else 1.0 if k == N_int else 2 * theta[k] ** 2 / theta[N_int] ** 2
    )
    assert abs(function_coefficients[k] - expected_function) <= 1e-5
    print(f"k={k}: candidate coefficient max discrepancy {error:.3g}")
    if expected.size:
        pf.pprint_labeled_matrix(expected, V_k_basis_labels(k))


# %%
def V_k_structure(k):
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    expression = sum(
        (float(C[i, j]) * vectors[i] * vectors[j] for i, j in np.ndindex(C.shape)),
        pf.Scalar.zero(),
    )
    if k:
        expression += function_coefficients[k] * (
            obj(ctx[f"x_{k}"]) - obj(ctx["x_star"])
        )
    return expression


component_residuals = {}
for k in required_indices:
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    errors = {}
    for name, residual, target_component in [
        ("gram", diff.inner_prod_coords, target.inner_prod_coords),
        ("function", diff.func_coords, target.func_coords),
        ("offset", diff.offset, target.offset),
    ]:
        error = float(np.max(np.abs(np.asarray(residual, dtype=float)), initial=0))
        scale = float(
            np.max(np.abs(np.asarray(target_component, dtype=float)), initial=0)
        )
        assert error <= 1e-4 + 1e-5 * scale
        errors[name] = error
    component_residuals[str(k)] = errors
    print(f"k={k}: full-component reconstruction", errors)
