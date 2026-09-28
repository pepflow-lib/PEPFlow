"""Update B2 notebook cells using the coherent saved certificate."""

import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
SUP = ROOT / "supplementary"
path = ROOT / "dual_feg_example_lyap.ipynb"
s = json.loads((ROOT / "state/dual_feg_b2.json").read_text())
tags = (
    [f"x_{k}" for k in range(s["N"] + 1)]
    + ["x_star"]
    + [f"y_{k}" for k in range(s["N"])]
)
for group, data in s["lambda_groups"].items():
    matrix = [[0.0 for _ in tags] for _ in tags]
    for name, val in zip(data["constraint_names"], data["values"]):
        a, b = name.split(":")[1].split(",")
        matrix[tags.index(a)][tags.index(b)] = 0.0 if val is None else val
    data.update(matrix=matrix, row_names=tags, col_names=tags)
for name in ["dual_feg_b2.json", "dual_feg_relaxed.json"]:
    (ROOT / "state" / name).write_text(json.dumps(s, indent=2))
nb = nbformat.read(path, as_version=4)
md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell
cells = [
    md(
        "## Full PEP certificate\nThe selected certificate uses the normalized sample $L=R=1$, $N=6$. Dense and sparse primal SDPs were solved with CLARABEL defaults. All selected duals and the Gram remainder come from one sparse solve."
    ),
    code("""dense = json.loads((NOTEBOOK_DIR / "state/dual_feg_dense.json").read_text())
certificate = json.loads((NOTEBOOK_DIR / "state/dual_feg_b2.json").read_text())
print("Dense bound:", dense["opt_value"], dense["solver_status"])
print("Selected sparse bound:", certificate["opt_value"], certificate["solver_status"])
print("Basis:", certificate["basis_vectors"])
print("Dropped constraints:", len(certificate["relaxed_constraints"]))
print("Preserved-optimum gap:", abs(dense["opt_value"] - certificate["opt_value"]))
for data, label in [(dense, "dense"), (certificate, "sparse")]:
    for group in sorted({m["group"] for m in data["constraint_metadata"].values() if m["group"]}):
        entries = [(n, v) for n, v in data["named_dual_values"].items()
                   if data["constraint_metadata"][n]["group"] == group and v is not None and abs(v) > 1e-6]
        print(label, group, "significant terms:", entries)"""),
    md(r"""### Sparse pattern and initial formula search
Keep terminal-point monotonicity against $x_\star$ and $y_k=x_{k+1/2}$ for $0\leq k<N-1$, and Lipschitz constraints between $x_k,y_k$ for $k<N-1$, with the final pair $x_{N-1},x_N$. All others are dropped. The final auxiliary evaluation at $y_{N-1}=x_N$ is not required by this relaxation.

Rational inspection suggests terminal-star multiplier $4/N$, terminal-$y_k$ multiplier $4/[(N-k)(N-k-1)]$, and Lipschitz multiplier $2/(N-k)^2$. These are normalized-sample candidates. The initial multiplier is $4/N^2$.

The low-rank remainder suggests
$$S_{\rm guess}=\left\|\frac{2}{N}(x_0-x_\star)-A(x_N)\right\|^2.$$
No target references were consulted. Numerical comparisons do not establish these formulas for arbitrary horizons."""),
    code("""N_cert = certificate["N"]
ctx_cert, pb_cert, A_cert = get_pep_setup(N_cert, {"L": 1, "R": 1})
pm_cert = pf.ExpressionManager(ctx_cert, resolve_parameters={"L": 1, "R": 1})
lambda_guess = {"initial_condition": 4/N_cert**2, f"A monotone:x_{N_cert},x_star": 4/N_cert}
lambda_guess.update({f"A monotone:x_{N_cert},y_{k}": 4/((N_cert-k)*(N_cert-k-1)) for k in range(N_cert-1)})
lambda_guess.update({f"A Lipschitz:x_{k},y_{k}": 2/(N_cert-k)**2 for k in range(N_cert-1)})
lambda_guess[f"A Lipschitz:x_{N_cert-1},x_{N_cert}"] = 2
active_names = [n for n,v in certificate["named_dual_values"].items() if v is not None]
lambda_error = max(abs(lambda_guess[n]-certificate["named_dual_values"][n]) for n in active_names)
pf.pprint_labeled_matrix(np.array([[lambda_guess[n]] for n in active_names]), row_labels=active_names, column_labels=["candidate"])
print("Candidate lambda maximum error:", lambda_error)
assert lambda_error <= 1e-4
S_array = np.asarray(certificate["S_matrix"])
w_guess = 2/N_cert*(ctx_cert["x_0"]-ctx_cert["x_star"])-A_cert(ctx_cert[f"x_{N_cert}"])
S_guess_eval = pm_cert.eval_scalar(w_guess**2)
S_guess = np.asarray(S_guess_eval.inner_prod_coords, dtype=float)
print("S candidate error:", np.max(np.abs(S_guess-S_array)))
assert np.allclose(S_guess, S_array, atol=1e-4, rtol=1e-5)
assert np.max(np.abs(S_guess_eval.func_coords), initial=0) == 0
assert S_guess_eval.offset == 0
support = [0, 1, len(certificate["basis_vectors"])-1]
pf.pprint_labeled_matrix(S_guess[np.ix_(support,support)], row_labels=[certificate["basis_vectors"][i] for i in support])
print("Candidate S has no other nonzero coordinates.")"""),
    md(
        "### Selected numerical decomposition\nReverse LDL preserves the complete saved remainder, including small pivots. No pivot or multiplier has been discarded from the certificate."
    ),
    code("""D = np.asarray(certificate["numerical_decomposition"]["D"])
E = np.asarray(certificate["numerical_decomposition"]["ell_coords"])
print("Reverse LDL diagonal:", np.diag(D))
print("Selected S rank at tolerance 1e-4:", np.linalg.matrix_rank(S_array, tol=1e-4))
pf.pprint_labeled_matrix(E, row_labels=[f"ell_{i}" for i in range(len(E))], column_labels=certificate["basis_vectors"])
print("S reconstruction maximum error:", np.max(np.abs(E.T@D@E-S_array)))
assert np.allclose(E.T@D@E, S_array, atol=1e-4, rtol=1e-5)"""),
    md(r"""### Complete numerical certificate check
For every retained scalar constraint let $r_c\leq0$ be its normalized residual. The certificate identity is
$$\mathrm{metric}-\mathrm{bound}-\sum_c\lambda_c r_c+S=0.$$
The following cell rebuilds every residual from the setup, checks its stored coordinates, and checks Gram, function and constant components. It also verifies the signs and positive semidefiniteness required for the bound."""),
    code("""entries = list(pb_cert.init_conditions) + A_cert.get_interpolation_constraints(ctx_cert)
assert {c.name for c in entries} == set(certificate["named_dual_values"])
weighted = pf.Scalar.zero()
for constraint in entries:
    name = constraint.name
    meta = certificate["constraint_metadata"][name]
    value = certificate["named_dual_values"][name]
    residual = constraint.lhs-constraint.rhs
    if constraint.cmp.value in ("GE", "SEQ"):
        residual = -residual
    evaluated = pm_cert.eval_scalar(pf.Scalar.zero()+residual)
    saved = certificate["constraint_coordinates"][name]
    assert np.allclose(evaluated.inner_prod_coords, saved["gram"], atol=1e-12, rtol=0)
    assert np.allclose(evaluated.func_coords, saved["func"], atol=1e-12, rtol=0)
    assert abs(float(evaluated.offset)-saved["offset"]) <= 1e-12
    if meta["relaxed"]:
        assert value is None
    else:
        assert value is not None and np.isfinite(value) and value >= -1e-6
        weighted += value * (pf.Scalar.zero()+residual)
basis_cert = ctx_cert.basis_vectors()
S_numeric = sum((float(S_array[i,j])*basis_cert[i]*basis_cert[j]
                 for i,j in np.ndindex(S_array.shape)), pf.Scalar.zero())
checked = pm_cert.eval_scalar(pb_cert.performance_metric-certificate["opt_value"]-weighted+S_numeric)
residuals = [float(np.max(np.abs(checked.inner_prod_coords))),
             float(np.max(np.abs(checked.func_coords),initial=0)),
             abs(float(checked.offset))]
print("Gram/function/offset identity residuals:", residuals)
pf.pprint_labeled_matrix(np.asarray(checked.inner_prod_coords, dtype=float), row_labels=certificate["basis_vectors"])
assert max(residuals) <= 1e-5
assert np.isfinite(S_array).all() and np.allclose(S_array,S_array.T,atol=1e-6,rtol=0)
assert np.linalg.eigvalsh(S_array).min() >= -1e-6
assert certificate["solver_status"] == "optimal"
assert abs(certificate["opt_value"]-dense["opt_value"]) <= 1e-5
assert abs(certificate["opt_value"]-4/N_cert**2) <= 1e-5
print("Numerical certificate verified; analytic full-PEP and Lyapunov proofs remain unverified.")"""),
]
index = next(
    i for i, c in enumerate(nb.cells) if c.source.startswith("## Full PEP certificate")
)
nb.cells[index : index + 1] = cells
nbformat.write(nb, path)
print("Updated cells", index, "through", index + len(cells) - 1)
