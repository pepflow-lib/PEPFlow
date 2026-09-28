# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import hashlib

import sympy as sp

b1 = json.loads((notebook_dir / "state" / "pgm_b1.json").read_text())
dense = json.loads((notebook_dir / "supplementary" / "N6" / "dense.json").read_text())
selected = json.loads(
    (notebook_dir / "supplementary" / "N6" / "sparse-candidate.json").read_text()
)
N_int = selected["N_verify"]
N = sp.S(N_int)
ctx, pb, obj = get_pep_setup(N_int, {"L": 1, "R": 1})
entries = [(c, "initial", None, None) for c in pb.init_conditions]
for owner in ctx.func_to_triplets:
    owner.get_interpolation_constraints(ctx)
    groups = ctx.get_constraint_data(owner)
    entries.extend(
        (c, "interpolation", str(owner), str(group))
        for group, constraints in groups.sc_dict.items()
        for c in constraints
    )
assert {c.name for c, *_ in entries} == set(selected["constraint_metadata"])
assert selected["basis_vectors"] == [str(v) for v in ctx.basis_vectors()]
assert selected["basis_scalars"] == [str(v) for v in ctx.basis_scalars()]
relaxed = []
for c, origin, *_ in entries:
    if origin == "initial":
        continue
    left, right = c.name.split(":")[1].split(",")
    keep = left == "x_star"
    if left != "x_star" and right != "x_star":
        keep = int(right.split("_")[1]) == int(left.split("_")[1]) + 1
    if not keep:
        relaxed.append(c.name)
assert relaxed == selected["relaxed_constraints"]
pb.set_relaxed_constraints(relaxed)
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S(1), "R": sp.S(1)})
S_array = np.asarray(selected["S_matrix"], dtype=float)
basis = ctx.basis_vectors()
print("Dense optimum:", dense["opt_value"])
print("Sparse optimum:", selected["opt_value"])
print("Dense/sparse difference:", abs(dense["opt_value"] - selected["opt_value"]))
print("Basis:", selected["basis_vectors"])
for sample_name, sample in [("dense", dense), ("sparse", selected)]:
    for owner_name in ("f", "g"):
        active = [
            (name, value)
            for name, value in sample["named_dual_values"].items()
            if name.startswith(owner_name + ":") and value is not None and value > 1e-6
        ]
        print(sample_name, owner_name, "active multipliers:", len(active))
    eig = np.linalg.eigvalsh(np.asarray(sample["S_matrix"]))
    print(
        sample_name, "S rank at 1e-4:", np.sum(np.abs(eig) > 1e-4), "eigenvalues:", eig
    )


def candidate_multiplier(name, horizon):
    horizon = sp.S(horizon)
    if name == "initial_condition":
        return sp.S(1) / (4 * horizon)
    owner, pair = name.split(":")
    left, right = pair.split(",")
    if left == "x_star":
        j = int(right.split("_")[1])
        if j == horizon:
            return sp.S(1 if owner == "f" else 2) / (horizon + 1)
        return (2 * horizon + (1 if owner == "f" else 0)) / (
            (2 * horizon - j) * (2 * horizon + 1 - j)
        )
    if right == "x_star":
        return sp.S(0)
    i, j = int(left.split("_")[1]), int(right.split("_")[1])
    return (
        (i + (1 if owner == "f" else 0)) / (2 * horizon - i) if j == i + 1 else sp.S(0)
    )


lambda_errors = []
for name, value in selected["named_dual_values"].items():
    candidate = candidate_multiplier(name, N)
    if value is not None:
        error = abs(float(candidate) - value)
        lambda_errors.append(error)
        print(name, "numerical=", round(value, 9), "candidate=", candidate)
    else:
        assert candidate == 0
print("Maximum multiplier comparison error:", max(lambda_errors))
assert max(lambda_errors) < 1e-4
for owner_name, indices in [
    ("f", ["star", *range(N_int + 1)]),
    ("g", ["star", *range(1, N_int + 1)]),
]:
    labels = [f"x_{i}" for i in indices]
    candidate_matrix = sp.Matrix(
        [
            [
                0 if a == b else candidate_multiplier(f"{owner_name}:{a},{b}", N)
                for b in labels
            ]
            for a in labels
        ]
    )
    pf.pprint_labeled_matrix(np.asarray(candidate_matrix, dtype=object), labels, labels)


S_candidate = pf.Scalar.zero()
square_vectors, square_coefficients, pieces = [], [], []
for ii in range(1, N_int + 1):
    i = sp.S(ii)
    a = f.grad(ctx[f"x_{ii}"])
    ap = f.grad(ctx[f"x_{ii - 1}"])
    ast = f.grad(ctx["x_star"])
    s = g.grad(ctx[f"x_{ii}"])
    c1 = N / ((2 * N + 1 - i) * (2 * N - i) * L)
    u1 = i / (2 * N) * a + (2 * N - i) / (2 * N) * ap - ast
    c2 = (
        (i - 1) / (2 * N - i) * (2 * N + 2) / (2 * N + 1)
        + 2 * N / ((2 * N - i) ** 2 * (2 * N + 1))
    ) / (2 * L)
    u2 = ap + s - L / (2 * N + 1 - i) * (ctx[f"x_{ii - 1}"] - ctx["x_star"])
    c3 = i / (2 * N + 1 - i) * (2 * N) / (2 * N + 1) / (2 * L)
    u3 = (
        (2 * N + 1) / (2 * N) * (a + s)
        - (ap + s) / (2 * N)
        - L / (2 * N - i) * (ctx[f"x_{ii}"] - ctx["x_star"])
    )
    piece = c1 * u1**2 + c2 * u2**2 + c3 * u3**2
    S_candidate += piece
    pieces.append(piece)
    square_vectors.extend([u1, u2, u3])
    square_coefficients.extend([c1, c2, c3])
E = np.asarray([pm.eval_vector(v).coords for v in square_vectors], dtype=float)
D = np.diag([float(c.get_value({"L": sp.S(1)})) for c in square_coefficients])
candidate_eval = pm.eval_scalar(S_candidate)
S_reconstructed = E.T @ D @ E


def max_abs(values):
    return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0.0))


print("Supplied SOS reconstruction residual:", max_abs(S_reconstructed - S_array))
assert np.allclose(S_reconstructed, S_array, atol=1e-4, rtol=1e-5)
assert max_abs(candidate_eval.func_coords) == 0 and max_abs(candidate_eval.offset) == 0
pf.pprint_labeled_matrix(
    S_reconstructed, selected["basis_vectors"], selected["basis_vectors"]
)


weighted = pf.Scalar.zero()
exact_weighted = pf.Scalar.zero()
inequality_duals = []
for c, *_ in entries:
    value = selected["named_dual_values"][c.name]
    residual = c.lhs - c.rhs
    if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
        residual = -residual
    meta = selected["constraint_metadata"][c.name]
    assert meta["comparator"] == c.cmp.value and meta["kind"] == "scalar"
    if meta["relaxed"]:
        assert value is None
        continue
    assert value is not None
    weighted += value * residual
    exact_weighted += candidate_multiplier(c.name, N) * residual
    if c.cmp != pf.Comparator.EQ:
        inequality_duals.append(value)
S_saved = sum(
    (float(S_array[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S_array.shape)),
    pf.Scalar.zero(),
)
assert pb.performance_metric is not None
checked = pm.eval_scalar(
    pb.performance_metric - selected["opt_value"] - weighted + S_saved
)
candidate_checked = pm.eval_scalar(
    pb.performance_metric - selected["opt_value"] - weighted + S_candidate
)
exact_checked = pm.eval_scalar(
    pb.performance_metric - sp.S(1) / (4 * N) - exact_weighted + S_candidate,
    sympy_mode=True,
)
exact_fixed_horizon = all(
    sp.simplify(v) == 0
    for values in (
        exact_checked.inner_prod_coords,
        exact_checked.func_coords,
        [exact_checked.offset],
    )
    for v in np.asarray(values, dtype=object).flat
)
residuals = dict(
    identity_gram_max_abs=max_abs(checked.inner_prod_coords),
    identity_func_max_abs=max_abs(checked.func_coords),
    identity_offset_abs=max_abs(checked.offset),
    S_reconstruction_max_abs=max_abs(S_reconstructed - S_array),
    candidate_identity_gram_max_abs=max_abs(candidate_checked.inner_prod_coords),
    dense_relaxed_gap=abs(dense["opt_value"] - selected["opt_value"]),
    conjecture_gap=abs(selected["opt_value"] - 1 / (4 * N_int)),
    minimum_scalar_inequality_dual=min(inequality_duals),
    minimum_S_eigenvalue=float(np.linalg.eigvalsh(S_array).min()),
    minimum_matrix_inequality_eigenvalue=0.0,
)
tolerances = json.loads((repo_root / "settings.json").read_text())["tolerances"]
assert selected["certificate_provenance"]["solver_status"] == "optimal"
assert np.all(np.isfinite(S_array)) and np.allclose(
    S_array, S_array.T, atol=1e-6, rtol=0
)
assert all(
    residuals[k] <= 1e-5
    for k in (
        "identity_gram_max_abs",
        "identity_func_max_abs",
        "identity_offset_abs",
        "candidate_identity_gram_max_abs",
    )
)
assert np.allclose(S_reconstructed, S_array, atol=1e-4, rtol=1e-5)
assert residuals["dense_relaxed_gap"] < 1e-5 and residuals["conjecture_gap"] < 1e-5
assert residuals["minimum_scalar_inequality_dual"] >= -1e-6
assert residuals["minimum_S_eigenvalue"] >= -1e-6
assert exact_fixed_horizon
print("Numerical certificate verified:", True)
print("Residuals:", residuals)
print("Exact candidate identity at N=6:", exact_fixed_horizon)
print("Analytic full-PEP proof for arbitrary N:", False)
pf.pprint_labeled_matrix(
    np.asarray(checked.inner_prod_coords),
    selected["basis_vectors"],
    selected["basis_vectors"],
)


source_paths = [
    notebook_dir / "pgm_setup.py",
    notebook_dir / "supplementary" / "helpers" / "certificates.py",
]
approved_list = json.loads((repo_root / "allowlist.json").read_text())[
    "exact_read_files"
]
source_paths.extend(
    Path(p) for p in approved_list if Path(p).parent == repo_root / "pepflow"
)
source_hashes = {
    str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths
}
assert selected["certificate_provenance"]["source_hashes"] == source_hashes
selected.update(b1)
selected.update(
    N=N_int,
    N_verify=N_int,
    numerical_certificate_verified=True,
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=False,
    proof_valid=True,
    require_analytic_full_pep=False,
)
selected["normalization"] = dict(
    tau_name="initial_condition",
    initial_condition=b1["initial_condition"],
    performance_metric=b1["performance_metric"],
    bound_value=selected["opt_value"],
    bound_formula=b1["conjectured_rate"],
    supplied_sos_scale=1,
)
selected["numerical_checks"] = dict(
    tolerances=tolerances,
    residuals=residuals,
    passed=True,
    exact_candidate_fixed_horizon=bool(exact_fixed_horizon),
)
selected["numerical_decomposition"] = dict(
    method="direct",
    D=D.tolist(),
    ell_coords=E.tolist(),
    basis_labels=selected["basis_vectors"],
    supplied_assistance=True,
    pieces=[
        np.asarray(pm.eval_scalar(piece).inner_prod_coords, dtype=float).tolist()
        for piece in pieces
    ],
)
selected["S_decomp_type"] = "direct"
selected["formula_status"] = {"lambda": "candidate", "S": "candidate"}
selected["closed_form_search"] = dict(
    completed=True,
    references_reviewed=["approved/input.md: supplied fixed SOS"],
    attempts=[
        "Sparse consecutive/star pattern preserves dense bound",
        "Rationalized consecutive multipliers; star coefficients derived by function-value conservation",
        "Supplied SOS compared to same numerical slack with scale 1",
        "Exact candidate full-coordinate identity verified at N=6",
    ],
    unresolved_components=["arbitrary-horizon analytic full-PEP identity"],
    multiplier_max_error=max(lambda_errors),
    S_max_error=residuals["S_reconstruction_max_abs"],
)
lambda_labels = ["x_star", *[f"x_{i}" for i in range(N_int + 1)]]
selected["lambda_row_names"] = lambda_labels
selected["lambda_col_names"] = lambda_labels
selected["lambda_matrix"] = [
    [selected["named_dual_values"].get(f"f:{a},{b}") or 0.0 for b in lambda_labels]
    for a in lambda_labels
]
print("Ready to serialize coherent B2 certificate.")


selected["lamb_code"] = (
    "def candidate_multiplier(name, horizon):\n    horizon = sp.S(horizon)\n    if name == 'initial_condition':\n        return sp.S(1)/(4*horizon)\n    owner, pair = name.split(':')\n    left, right = pair.split(',')\n    if left == 'x_star':\n        j = int(right.split('_')[1])\n        if j == horizon:\n            return sp.S(1 if owner == 'f' else 2)/(horizon+1)\n        return (2*horizon + (1 if owner == 'f' else 0))/((2*horizon-j)*(2*horizon+1-j))\n    if right == 'x_star':\n        return sp.S(0)\n    i, j = int(left.split('_')[1]), int(right.split('_')[1])\n    return (i + (1 if owner == 'f' else 0))/(2*horizon-i) if j == i+1 else sp.S(0)\n\nlambda_errors = []\nfor name, value in selected['named_dual_values'].items():\n    candidate = candidate_multiplier(name, N)\n    if value is not None:\n        error = abs(float(candidate)-value)\n        lambda_errors.append(error)\n        print(name, 'numerical=', round(value, 9), 'candidate=', candidate)\n    else:\n        assert candidate == 0\nprint('Maximum multiplier comparison error:', max(lambda_errors))\nassert max(lambda_errors) < 1e-4\nfor owner_name, indices in [('f', ['star', *range(N_int+1)]), ('g', ['star', *range(1, N_int+1)])]:\n    labels = [f'x_{i}' for i in indices]\n    candidate_matrix = sp.Matrix([[0 if a == b else candidate_multiplier(f'{owner_name}:{a},{b}', N)\n                                  for b in labels] for a in labels])\n    pf.pprint_labeled_matrix(np.asarray(candidate_matrix, dtype=object), labels, labels)\n"
)
selected["S_code"] = (
    "S_candidate = pf.Scalar.zero()\nsquare_vectors, square_coefficients, pieces = [], [], []\nfor ii in range(1, N_int+1):\n    i = sp.S(ii)\n    a = f.grad(ctx[f'x_{ii}'])\n    ap = f.grad(ctx[f'x_{ii-1}'])\n    ast = f.grad(ctx['x_star'])\n    s = g.grad(ctx[f'x_{ii}'])\n    c1 = N / ((2*N+1-i)*(2*N-i)*L)\n    u1 = i/(2*N)*a + (2*N-i)/(2*N)*ap - ast\n    c2 = ((i-1)/(2*N-i)*(2*N+2)/(2*N+1) + 2*N/((2*N-i)**2*(2*N+1)))/(2*L)\n    u2 = ap+s-L/(2*N+1-i)*(ctx[f'x_{ii-1}']-ctx['x_star'])\n    c3 = i/(2*N+1-i)*(2*N)/(2*N+1)/(2*L)\n    u3 = (2*N+1)/(2*N)*(a+s)-(ap+s)/(2*N)-L/(2*N-i)*(ctx[f'x_{ii}']-ctx['x_star'])\n    piece = c1*u1**2 + c2*u2**2 + c3*u3**2\n    S_candidate += piece\n    pieces.append(piece)\n    square_vectors.extend([u1, u2, u3])\n    square_coefficients.extend([c1, c2, c3])\nE = np.asarray([pm.eval_vector(v).coords for v in square_vectors], dtype=float)\nD = np.diag([float(c.get_value({'L': sp.S(1)})) for c in square_coefficients])\ncandidate_eval = pm.eval_scalar(S_candidate)\nS_reconstructed = E.T @ D @ E\ndef max_abs(values):\n    return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0.0))\nprint('Supplied SOS reconstruction residual:', max_abs(S_reconstructed - S_array))\nassert np.allclose(S_reconstructed, S_array, atol=1e-4, rtol=1e-5)\nassert max_abs(candidate_eval.func_coords) == 0 and max_abs(candidate_eval.offset) == 0\npf.pprint_labeled_matrix(S_reconstructed, selected['basis_vectors'], selected['basis_vectors'])\n"
)
selected["certificate_check_code"] = (
    "weighted = pf.Scalar.zero()\nexact_weighted = pf.Scalar.zero()\ninequality_duals = []\nfor c, *_ in entries:\n    value = selected['named_dual_values'][c.name]\n    residual = c.lhs-c.rhs\n    if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):\n        residual = -residual\n    meta = selected['constraint_metadata'][c.name]\n    assert meta['comparator'] == c.cmp.value and meta['kind'] == 'scalar'\n    if meta['relaxed']:\n        assert value is None\n        continue\n    assert value is not None\n    weighted += value * residual\n    exact_weighted += candidate_multiplier(c.name, N)*residual\n    if c.cmp != pf.Comparator.EQ:\n        inequality_duals.append(value)\nS_saved = sum((float(S_array[i,j])*basis[i]*basis[j] for i,j in np.ndindex(S_array.shape)), pf.Scalar.zero())\nassert pb.performance_metric is not None\nchecked = pm.eval_scalar(pb.performance_metric-selected['opt_value']-weighted+S_saved)\ncandidate_checked = pm.eval_scalar(pb.performance_metric-selected['opt_value']-weighted+S_candidate)\nexact_checked = pm.eval_scalar(pb.performance_metric-sp.S(1)/(4*N)-exact_weighted+S_candidate, sympy_mode=True)\nexact_fixed_horizon = all(sp.simplify(v) == 0 for values in\n                         (exact_checked.inner_prod_coords, exact_checked.func_coords, [exact_checked.offset])\n                         for v in np.asarray(values, dtype=object).flat)\nresiduals = dict(identity_gram_max_abs=max_abs(checked.inner_prod_coords),\n    identity_func_max_abs=max_abs(checked.func_coords), identity_offset_abs=max_abs(checked.offset),\n    S_reconstruction_max_abs=max_abs(S_reconstructed-S_array),\n    candidate_identity_gram_max_abs=max_abs(candidate_checked.inner_prod_coords),\n    dense_relaxed_gap=abs(dense['opt_value']-selected['opt_value']),\n    conjecture_gap=abs(selected['opt_value']-1/(4*N_int)),\n    minimum_scalar_inequality_dual=min(inequality_duals),\n    minimum_S_eigenvalue=float(np.linalg.eigvalsh(S_array).min()),\n    minimum_matrix_inequality_eigenvalue=0.0)\ntolerances = json.loads((repo_root / 'settings.json').read_text())['tolerances']\nassert selected['certificate_provenance']['solver_status'] == 'optimal'\nassert np.all(np.isfinite(S_array)) and np.allclose(S_array, S_array.T, atol=1e-6, rtol=0)\nassert all(residuals[k] <= 1e-5 for k in ('identity_gram_max_abs', 'identity_func_max_abs', 'identity_offset_abs', 'candidate_identity_gram_max_abs'))\nassert np.allclose(S_reconstructed, S_array, atol=1e-4, rtol=1e-5)\nassert residuals['dense_relaxed_gap'] < 1e-5 and residuals['conjecture_gap'] < 1e-5\nassert residuals['minimum_scalar_inequality_dual'] >= -1e-6\nassert residuals['minimum_S_eigenvalue'] >= -1e-6\nassert exact_fixed_horizon\nprint('Numerical certificate verified:', True)\nprint('Residuals:', residuals)\nprint('Exact candidate identity at N=6:', exact_fixed_horizon)\nprint('Analytic full-PEP proof for arbitrary N:', False)\npf.pprint_labeled_matrix(np.asarray(checked.inner_prod_coords), selected['basis_vectors'], selected['basis_vectors'])\n"
)
certificate_keys = (
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
selected["certificate_id"] = hashlib.sha256(
    json.dumps(
        {key: selected[key] for key in certificate_keys},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
).hexdigest()
for filename in ("pgm_relaxed.json", "pgm_b2.json"):
    (notebook_dir / "supplementary" / "N6" / filename).write_text(
        json.dumps(selected, indent=2, allow_nan=False)
    )
print("Saved certificate ID:", selected["certificate_id"])
