import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import json
import os

# optional notebook-generation dependency
import nbformat as nb  # ty: ignore[unresolved-import]
import runtime

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
path = root / "pgm_example_lyap.ipynb"
book = nb.read(path, as_version=4)
source = (root / "supplementary/helpers/candidates.py").read_text()
new = [
    nb.v4.new_markdown_cell(r"""## Dense and relaxed proof solves
At $N=6$ the dense and relaxed PEPs use CLARABEL defaults. We retain $f$ and $g$ inequalities from the optimum to each sampled iterate and from each iterate to its successor; all other inequalities are dropped. Each chosen certificate component comes from one solve. The stored dense/relaxed data below are solver outputs, and subsequent cells recheck their full identity without resolving the optimization problem."""),
    nb.v4.new_code_cell('''import hashlib
import sympy as sp

dense = json.loads((notebook_dir / "state/pgm_dense.json").read_text())
b2 = json.loads((notebook_dir / "state/pgm_b2.json").read_text())
N = b2["N_verify"]
print("Dense:", dense["opt_value"], dense["status"])
print("Relaxed:", b2["opt_value"], b2["certificate_provenance"]["solver_status"])
print("Dense-relaxed difference:", abs(dense["opt_value"] - b2["opt_value"]))
print("Basis:", b2["basis_vectors"])
for owner in ("f", "g"):
    entries_owner = [(name, value) for name, value in dense["duals"].items()
                     if name.startswith(owner + ":") and abs(value) > 1e-6]
    print(owner, "dense active entries:", len(entries_owner), "largest:",
          sorted(entries_owner, key=lambda row: -row[1])[:4])
print("Dense S eigenvalues:", np.linalg.eigvalsh(np.array(dense["S_matrix"])))
print("Dropped constraint count:", len(b2["relaxed_constraints"]))
for name, value in b2["named_dual_values"].items():
    if value is not None:
        print(name, value)
assert abs(dense["opt_value"] - b2["opt_value"]) < 1e-5
assert b2["certificate_provenance"]["solver_status"] == "optimal"'''),
    nb.v4.new_markdown_cell(r"""## Lambda and S verification
Define all interpolation residuals with sign $R\le0$. The numerical certificate is
$$h(x_N)-h(x_\star)-\mathrm{opt}-\sum_q\lambda_qR_q+S=0.$$
The sum includes the radius constraint. Inequality multipliers and the Gram slack must be nonnegative and positive semidefinite, respectively.

The sparse fractions suggest $f$ successor multipliers $(i+1)/(2N-i)$ and $g$ successor multipliers $i/(2N-i)$. Optimum-to-iterate multipliers are their consecutive differences, with endpoint adjustments. The following executable definitions include all endpoints. They are candidates for arbitrary $N$, not yet an all-horizon proof. The supplied SOS aid has normalization factor 1 in this objective-gap certificate. Its positive coefficients use exact rational expressions; the notebook verifies reconstruction against the same selected numerical slack."""),
    nb.v4.new_code_cell(source[source.index("def aid_pieces") :]),
    nb.v4.new_code_cell("""from pepflow.parameter import eval_parameter

ctx_b2, pb_b2, obj_b2 = get_pep_setup(N, {"L": 1, "R": 1})
entries = [(c, "initial", None, None) for c in pb_b2.init_conditions]
for owner in ctx_b2.func_to_triplets:
    owner.get_interpolation_constraints(ctx_b2)
    groups = ctx_b2.get_constraint_data(owner)
    entries.extend((c, "interpolation", str(owner), str(group))
                   for group, constraints in groups.sc_dict.items() for c in constraints)
    assert not groups.psd_dict, "Unexpected PSD interpolation extras"
assert len({c.name for c, *_ in entries}) == len(entries)
assert set(b2["named_dual_values"]) == {c.name for c, *_ in entries}
assert [str(v) for v in ctx_b2.basis_vectors()] == b2["basis_vectors"]
assert [str(v) for v in ctx_b2.basis_scalars()] == b2["basis_scalars"]
for filename, expected in b2["certificate_provenance"]["source_hashes"].items():
    assert hashlib.sha256(Path(filename).read_bytes()).hexdigest() == expected
certificate_keys = ("N_verify", "params_json", "relaxed_constraints", "S_matrix", "S_row_names",
    "S_col_names", "basis_vectors", "basis_scalars", "opt_value", "tau_sol", "tau_name",
    "named_dual_values", "constraint_metadata", "normalization", "certificate_provenance",
    "numerical_checks", "numerical_decomposition")
assert hashlib.sha256(json.dumps({k: b2[k] for k in certificate_keys}, sort_keys=True,
    separators=(",", ":"), allow_nan=False).encode()).hexdigest() == b2["certificate_id"]
expected_dropped = []
for c, *_ in entries:
    if c.name == "initial_condition":
        continue
    ri, ci = c.name.split(":")[1].split(",")
    keep = ri == "x_star" or (ci != "x_star" and int(ci[2:]) == int(ri[2:]) + 1)
    if not keep:
        expected_dropped.append(c.name)
assert set(expected_dropped) == set(b2["relaxed_constraints"])
pb_b2.set_relaxed_constraints(expected_dropped)
pm = pf.ExpressionManager(ctx_b2, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
pieces = aid_pieces(ctx_b2, f, g, L, N)
S_candidate = square_sum(pieces)
E = np.array([pm.eval_vector(u).coords for _, _, _, u in pieces], dtype=float)
D = np.diag(np.asarray([eval_parameter(c, {"L": sp.S.One}) for _, _, c, _ in pieces], dtype=float))
S_saved = np.array(b2["S_matrix"])
assert np.allclose(E.T @ D @ E, S_saved, atol=1e-4, rtol=1e-5)
assert np.min(np.diag(D)) >= 0
assert np.allclose(S_saved, S_saved.T, atol=1e-6, rtol=0)
assert np.min(np.linalg.eigvalsh(S_saved)) >= -1e-6
assert all(value is None or value >= -1e-6 for value in b2["named_dual_values"].values())
weighted = pf.Scalar.zero()
weighted_exact = pf.Scalar.zero()
for c, origin, owner, group in entries:
    meta = b2["constraint_metadata"][c.name]
    assert (meta["origin"], meta["owner"], meta["group"], meta["comparator"]) == (
        origin, owner, group, c.cmp.value)
    residual = c.lhs - c.rhs
    if c.cmp == pf.Comparator.GE:
        residual = -residual
    value = b2["named_dual_values"][c.name]
    if value is not None:
        weighted += value * residual
    else:
        assert c.name in expected_dropped
    weighted_exact += multiplier_candidate(c.name, N) * residual
residual_numeric = pm.eval_scalar(pb_b2.performance_metric - b2["opt_value"] - weighted + S_candidate)
def maxabs(values):
    return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0))

print("Full numerical identity residuals:", maxabs(residual_numeric.inner_prod_coords),
      maxabs(residual_numeric.func_coords), maxabs(residual_numeric.offset))
assert all(maxabs(v) <= 1e-5 for v in (residual_numeric.inner_prod_coords,
    residual_numeric.func_coords, residual_numeric.offset))
print("SOS reconstruction error:", maxabs(E.T @ D @ E - S_saved))
print("Minimum S eigenvalue:", np.min(np.linalg.eigvalsh(S_saved)))
pf.pprint_labeled_matrix(E.T @ D @ E, b2["basis_vectors"], b2["basis_vectors"], precision=4)
pf.pprint_labeled_matrix(np.asarray(residual_numeric.inner_prod_coords, dtype=float),
                        b2["basis_vectors"], b2["basis_vectors"], precision=8)
# Exact-mode fixed-N check; this is separate from the numerical certificate.
exact_manager = pf.ExpressionManager(ctx_b2, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
exact = exact_manager.eval_scalar(pb_b2.performance_metric - sp.Rational(1, 4*N)
    - weighted_exact + S_candidate, sympy_mode=True)
assert all(sp.simplify(v) == 0 for v in np.asarray(exact.inner_prod_coords).flat)
assert all(sp.simplify(v) == 0 for v in np.asarray(exact.func_coords).flat)
assert sp.simplify(exact.offset) == 0
print("Exact candidate fixed-N identity: all coordinates are zero")
for owner in ("f", "g"):
    tags = ["x_star"] + [f"x_{j}" for j in range(0 if owner == "f" else 1, N+1)]
    candidate_matrix = np.array([[sp.S.Zero if ri == ci else multiplier_candidate(
        f"{owner}:{ri},{ci}", N) for ci in tags] for ri in tags], dtype=object)
    pf.pprint_labeled_matrix(candidate_matrix, tags, tags)
candidate_error = max(abs(value - float(multiplier_candidate(name, N)))
    for name, value in b2["named_dual_values"].items() if value is not None)
assert candidate_error < 1e-4
print("Candidate multiplier error:", candidate_error)
print("Numerical certificate verified; arbitrary-horizon analytic proof remains pending.")"""),
    nb.v4.new_markdown_cell("""### Initial closed-form search status
Sparse consecutive multipliers were rationalized and their differences identified. Both function classes have candidate formulas, including endpoints. The supplied SOS reconstructs the same selected slack within the fixed tolerance; the candidate multipliers and SOS satisfy an exact fixed-$N$ identity above. This does not establish the identity for arbitrary horizons. Global analytic verification and the Lyapunov theorem remain pending."""),
]
book.cells = book.cells[:7] + new + book.cells[-3:]
nb.write(book, path)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(
    book,
    timeout=180,
    kernel_name="pgm-attempt",
    resources={"metadata": {"path": str(root)}},
).execute()
nb.write(book, path)
for c in book.cells:
    if c.cell_type == "markdown":
        assert not any(
            s in c.source for s in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r")
        )
# The newly executed exact-mode check supersedes the earlier roundoff-only candidate check.
for name in ("pgm_b2.json", "pgm_relaxed.json"):
    state = json.loads((root / "state" / name).read_text())
    state["candidate_fixed_N_exact_residual"] = 0
    state["closed_form_search"]["attempts"][0]["exact_mode"] = (
        "sympy_mode=True, all coordinates simplify exactly to zero in notebook"
    )
    (root / "state" / name).write_text(json.dumps(state, indent=2))
check = root / "supplementary/pgm_example_lyap_checklist.md"
t = check.read_text()
t = t.replace("Last reviewed block: B1", "Last reviewed block: B2")
import re  # noqa: E402 - imports follow runtime or notebook setup

t = re.sub(
    r"SHA-256: [a-f0-9]+",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    t,
)
t = t.replace(
    "| pending | 7 | Due B2. |",
    "| verified | 7,8 | Dense and coherent relaxed solve summaries, all owners and preserved optimum inspected. |",
)
t = t.replace(
    "| pending | 8 | Due B2. |",
    "| verified | 9,10,11,12 | Executed candidate definitions, complete numerical identity, signs, source and certificate hashes, SOS reconstruction and exact fixed-N check; global status pending. |",
)
t = (
    t.replace("| pending | 9 | Due B3. |", "| pending | 13 | Due B3. |")
    .replace("| pending | 10 | Due B4. |", "| pending | 14 | Due B4. |")
    .replace("| pending | 11 | Due B4/B5. |", "| pending | 15 | Due B4/B5. |")
    .replace("| pending | 11 | Due B5. |", "| pending | 15 | Due B5. |")
)
check.write_text(t)
print("B2 notebook executed; complete numerical and exact fixed-N checks passed.")
