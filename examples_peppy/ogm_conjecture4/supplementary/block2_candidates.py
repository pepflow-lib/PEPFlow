# Notebook code fragment; required globals are supplied by its caller.
# Retained for notebook execution or serialized proof/state source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Candidate formulas and exact elementary identities, embedded in the notebook."""


# %% Candidate lambda functions
def candidate_theta(n):
    values = [sp.Integer(1)]
    for k in range(n):
        factor = 8 if k == n - 1 else 4
        values.append(((1 + sp.sqrt(1 + factor * values[-1] ** 2)) / 2).evalf(50))
    return values


def candidate_weights(n):
    theta = candidate_theta(n)
    q = theta[n - 1] ** 2
    chain = [
        theta[i] ** 2 * (2 * q - theta[i] ** 2) / (q * (2 * q - theta[i] ** 2 + 1))
        for i in range(n)
    ]
    star = [chain[0], *[chain[i] - chain[i - 1] for i in range(1, n)], 1 - chain[-1]]
    return star, chain


def lamb(ri, ci, n):
    points = [f"x_{i}" for i in range(n)] + [f"y_{n}"]
    star, chain = candidate_weights(n)
    if ri == "x_star" and ci in points:
        return star[points.index(ci)]
    if ri in points[:-1] and ci == points[points.index(ri) + 1]:
        return chain[points.index(ri)]
    return sp.Integer(0)


candidate_lambda = np.array(
    [
        [float(lamb(ri, ci, N_int)) for ci in selected["lambda_col_names"]]
        for ri in selected["lambda_row_names"]
    ]
)
lambda_candidate_error = float(
    np.max(np.abs(candidate_lambda - np.asarray(selected["lambda_matrix"])))
)
assert lambda_candidate_error < 1e-4
print(
    "Candidate lambda maximum difference from selected solve:", lambda_candidate_error
)
pf.pprint_labeled_matrix(
    candidate_lambda,
    selected["lambda_row_names"],
    selected["lambda_col_names"],
    precision=6,
)


# %% Candidate S expression, kept separate from the selected numerical certificate
def candidate_S(context, builder, n, parameters):
    context.set_as_current()
    owner = next(iter(context.func_to_triplets))
    theta = candidate_theta(n)
    tau_candidate = sp.sympify(parameters["L"]) / (2 * (2 * theta[n - 1] ** 2 + 1))
    bound_candidate = tau_candidate * sp.sympify(parameters["R"]) ** 2
    initial = next(c for c in builder.init_conditions if c.name == "initial_condition")
    weighted = tau_candidate * (initial.lhs - initial.rhs)
    for constraint in owner.get_interpolation_constraints(context):
        ri, ci = constraint.name.split(":", 1)[1].split(",")
        weighted += lamb(ri, ci, n) * (constraint.lhs - constraint.rhs)
    return bound_candidate + weighted - builder.performance_metric


S_guess = candidate_S(ctx, pb, N_int, params_sp)
guess_eval = pm.eval_scalar(S_guess)
S_guess_array = np.asarray(guess_eval.inner_prod_coords, float)
S_candidate_error = float(np.max(np.abs(S_guess_array - S_array)))
candidate_component_checks = dict(
    gram_difference_from_selected=S_candidate_error,
    function_max_abs=max_abs(guess_eval.func_coords),
    offset_abs=max_abs(guess_eval.offset),
    minimum_eigenvalue=float(np.linalg.eigvalsh(S_guess_array).min()),
)
assert S_candidate_error < 1e-4
assert candidate_component_checks["function_max_abs"] < 1e-12
assert candidate_component_checks["offset_abs"] < 1e-12
print("Candidate S checks:", candidate_component_checks)
pf.pprint_labeled_matrix(S_guess_array, basis_labels, basis_labels, precision=6)
# The expression identity defines this candidate; positivity for all N remains open.
search_record = json.loads((HERE / "b2_formula_search.json").read_text())
print(
    "Rejected naive candidate minimum Schur eigenvalue:",
    search_record["candidates"][0]["schur_eigenvalues"][0],
)
print(
    "Closed-form vs linear null-equation reconstruction:",
    search_record["closed_form_vs_linear_null_solution_max_error"],
)
print("Recompute candidate checks for N=1..10 (algebra only; no SDP solves):")
candidate_sample_checks = []
for sample_n in range(1, 11):
    sample_ctx, sample_pb, _ = setup.get_pep_setup(sp.S(sample_n), {"L": 1, "R": 1})
    sample_expression = candidate_S(sample_ctx, sample_pb, sample_n, {"L": 1, "R": 1})
    sample_pm = pf.ExpressionManager(sample_ctx, resolve_parameters={"L": 1, "R": 1})
    sample_eval = sample_pm.eval_scalar(sample_expression)
    sample_matrix = np.asarray(sample_eval.inner_prod_coords, float)
    sample_a = np.array(candidate_weights(sample_n)[0], float)
    sample_tau = 1 / (2 * (2 * float(candidate_theta(sample_n)[sample_n - 1]) ** 2 + 1))
    sample_H = sample_matrix[2:, 2:] - np.outer(sample_a, sample_a) / (4 * sample_tau)
    sample_check = dict(
        N=sample_n,
        minimum_star_weight=float(sample_a.min()),
        function_residual=max_abs(sample_eval.func_coords),
        offset_residual=max_abs(sample_eval.offset),
        minimum_schur_eigenvalue=float(np.linalg.eigvalsh(sample_H).min()),
        null_residual=max_abs(sample_H @ np.ones(sample_n + 1)),
    )
    assert sample_check["minimum_star_weight"] >= 0
    assert sample_check["minimum_schur_eigenvalue"] >= -1e-10
    assert (
        sample_check["function_residual"] < 1e-12
        and sample_check["offset_residual"] < 1e-12
    )
    candidate_sample_checks.append(sample_check)
    print(sample_check)
ctx.set_as_current()

# %% Exact elementary identities behind the candidate weights
t, q, s = sp.symbols("t q s", positive=True)
p = t**2 - t
phi = lambda z: 2 * z - z**2 / q  # noqa: E731 - retain the archived numerical helper
exact_residuals = {
    "theta_product_step": sp.cancel((1 - 1 / t) - p / t**2),
    "weighted_theta_telescope": sp.expand((2 * t - 1) * t**2 - (t**4 - p**2)),
    "terminal_coefficient_telescope": sp.cancel(
        phi(t**2) - phi(p) - (2 * t - (2 * t - 1) * t**2 / q)
    ),
}
b_of_s = s * (2 * q - s) / (q * (2 * q - s + 1))
derivative = (1 - (2 * q + 1) / (2 * q - s + 1) ** 2) / q
exact_residuals["weight_derivative"] = sp.cancel(sp.diff(b_of_s, s) - derivative)
exact_residuals["terminal_weight"] = sp.cancel(1 - b_of_s.subs(s, q) - 1 / (q + 1))
# q>=1 and 0<=s<=q imply (2q-s+1)^2 >= (q+1)^2; the latter minus (2q+1) is q^2.
exact_residuals["derivative_numerator_lower_bound"] = sp.expand(
    (q + 1) ** 2 - (2 * q + 1) - q**2
)
assert all(value == 0 for value in exact_residuals.values())
print("Exact candidate-weight algebra residuals:", exact_residuals)
print(
    "Candidate weight nonnegativity follows on q>=1, 0<=s<=q; global Gram PSD remains unproved."
)
