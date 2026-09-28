"""Visible B2 notebook construction and checks, embedded verbatim into cells."""

LOAD = '''import hashlib
import sympy as sp

certificate_dir = globals().get("certificate_dir", notebook_dir / "state")
b2 = json.loads((certificate_dir / "ogm_b2.json").read_text())
dense = json.loads((certificate_dir / "ogm_dense.json").read_text())
N = b2["N_verify"]
params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.Integer(1), "R": sp.Integer(1)}
ctx, pb, obj = get_pep_setup(N, params_sp)
pb.set_relaxed_constraints(b2["relaxed_constraints"])
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
basis = ctx.basis_vectors()
assert [str(v) for v in basis] == b2["basis_vectors"]
assert [str(v) for v in ctx.basis_scalars()] == b2["basis_scalars"]
for relative, digest in b2["certificate_provenance"]["source_hashes"].items():
    assert hashlib.sha256((notebook_dir / relative).read_bytes()).hexdigest() == digest
certificate_keys = ('N_verify', 'params_json', 'relaxed_constraints', 'S_matrix', 'S_row_names',
    'S_col_names', 'basis_vectors', 'basis_scalars', 'opt_value', 'tau_sol', 'tau_name',
    'named_dual_values', 'constraint_metadata', 'normalization', 'certificate_provenance',
    'numerical_checks', 'numerical_decomposition')
assert hashlib.sha256(json.dumps({k: b2[k] for k in certificate_keys}, sort_keys=True,
    separators=(',', ':'), allow_nan=False).encode()).hexdigest() == b2["certificate_id"]
print("Dense bound:", dense["opt_value"])
print("Dense active interpolation multipliers:", {k: v for k, v in dense["named_dual_values"].items() if v is not None and v > 1e-6})
print("Basis:", b2["basis_vectors"])
print("Dense S eigenvalues:", np.linalg.eigvalsh(np.array(dense["S_matrix"])))
print("Selected bound:", b2["opt_value"], "solver:", b2["certificate_provenance"]["solver"])
assert abs(b2["opt_value"] - dense["opt_value"]) < 1e-5
assert abs(b2["opt_value"] - 1/(2*theta_sequence(N)[-1]**2)) < 1e-5

def point_index(tag):
    return -1 if tag == "x_star" else 0 if tag == "z_0" else int(tag.split("_")[-1])

reconstructed_relaxation = []
for name, meta in b2["constraint_metadata"].items():
    if meta["origin"] == "interpolation":
        ri, ci = name.split(":")[1].split(",")
        i, j = point_index(ri), point_index(ci)
        if not (i == -1 or (0 <= i < N and j == i+1)):
            reconstructed_relaxation.append(name)
assert reconstructed_relaxation == b2["relaxed_constraints"]
print("Dropped constraints:", len(reconstructed_relaxation), "; retained star row and forward chain")
print("All active selected multipliers:")
for name, value in b2["named_dual_values"].items():
    if value is not None:
        print(name, value)
'''

CANDIDATES = '''theta = theta_sequence(N)

def lamb(ri, ci):
    i, j = point_index(ri), point_index(ci)
    if i == -1 and j >= 0:
        return 1/theta[N] if j == N else 2*theta[j]/theta[N]**2
    if 0 <= i < N and j == i+1:
        return 2*theta[i]**2/theta[N]**2
    return 0.0

lambda_candidate = np.array([[lamb(ri, ci) for ci in b2["lambda_col_names"]]
                             for ri in b2["lambda_row_names"]])
lambda_error = float(np.max(np.abs(lambda_candidate - np.array(b2["lambda_matrix"]))))
assert lambda_error < 1e-4
pf.pprint_labeled_matrix(lambda_candidate, b2["lambda_row_names"], b2["lambda_col_names"])
S_guess = (ctx[f"z_{N}"] - ctx["x_star"] - (theta[N]/L)*ctx[f"g_{N}"])**2 * (L/(2*theta[N]**2))
guess_eval = pm.eval_scalar(S_guess)
S_array = np.array(b2["S_matrix"])
S_candidate = np.asarray(guess_eval.inner_prod_coords, dtype=float)
assert np.allclose(S_candidate, S_array, atol=1e-4, rtol=0)
assert np.max(np.abs(np.asarray(guess_eval.func_coords, dtype=float)), initial=0) < 1e-4
assert abs(float(guess_eval.offset)) < 1e-4
pf.pprint_labeled_matrix(S_candidate, b2["basis_vectors"])
print("Candidate lambda max error:", lambda_error)
print("Candidate S max error:", float(np.max(np.abs(S_candidate - S_array))))
print("Formula status: numerical candidates only; analytic all-horizon identities unresolved.")
'''

VERIFY = '''D = np.array(b2["numerical_decomposition"]["D"])
E = np.array(b2["numerical_decomposition"]["ell_coords"])
assert b2["numerical_decomposition"]["basis_labels"] == [str(v) for v in basis]
ell = [sum((float(a)*v for a, v in zip(row, basis)), pf.Vector.zero()) for row in E]
S_numeric = sum((float(D[i,j])*ell[i]*ell[j] for i,j in np.ndindex(D.shape)), pf.Scalar.zero())
S_reconstructed = E.T @ D @ E
assert np.allclose(S_reconstructed, S_array, atol=1e-4, rtol=1e-5)
print("Reverse LDL diagonal (all factors retained):", np.diag(D))
pf.pprint_labeled_matrix(S_reconstructed, b2["basis_vectors"])
print("S reconstruction max error:", float(np.max(np.abs(S_reconstructed - S_array))))

entries = [(c, "initial", None, None) for c in pb.init_conditions]
assert not ctx.oper_to_duplets
for owner in ctx.func_to_triplets:
    groups = ctx.get_constraint_data(owner)
    assert not groups.psd_dict
    entries.extend((c, "interpolation", str(owner), str(group))
        for group, constraints in groups.sc_dict.items() for c in constraints)
assert {c.name for c, *_ in entries} == set(b2["constraint_metadata"]) == set(b2["named_dual_values"])
weighted_constraints = pf.Scalar.zero()
inequality_values = []
for c, origin, owner, group in entries:
    assert isinstance(c, pf.ScalarConstraint)
    metadata = dict(origin=origin, owner=owner, group=group, kind="scalar", comparator=c.cmp.value,
                    shape=[], relaxed=c.name in pb.relaxed_constraints)
    assert metadata == b2["constraint_metadata"][c.name]
    value = b2["named_dual_values"][c.name]
    if metadata["relaxed"]:
        assert value is None
        continue
    assert value is not None and np.isfinite(value)
    residual = c.lhs-c.rhs
    if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
        residual = -residual
    weighted_constraints += float(value)*residual
    if c.cmp != pf.Comparator.EQ:
        inequality_values.append(float(value))
diff = pb.performance_metric-b2["opt_value"]-weighted_constraints+S_numeric
checked = pm.eval_scalar(diff)
gram_residual = np.asarray(checked.inner_prod_coords, dtype=float)
func_residual = np.asarray(checked.func_coords, dtype=float)
offset_residual = float(checked.offset)
assert b2["certificate_provenance"]["solver_status"] == "optimal"
assert np.max(np.abs(gram_residual), initial=0) <= 1e-5
assert np.max(np.abs(func_residual), initial=0) <= 1e-5
assert abs(offset_residual) <= 1e-5
assert min(inequality_values) >= -1e-6
assert np.all(np.isfinite(S_array)) and np.allclose(S_array, S_array.T, atol=1e-6, rtol=0)
assert np.linalg.eigvalsh(S_array).min() >= -1e-6
pf.pprint_labeled_matrix(gram_residual, b2["basis_vectors"], precision=10)
print("Identity Gram/function/offset maxima:", np.max(np.abs(gram_residual)), np.max(np.abs(func_residual)), abs(offset_residual))
print("Numerical certificate verified; analytic full PEP and Lyapunov proof remain unverified.")
'''
