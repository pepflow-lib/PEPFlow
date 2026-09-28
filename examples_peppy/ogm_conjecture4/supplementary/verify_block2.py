"""Reconstruct and verify the captured current-run certificate without a solve.

The mathematical body of this file is also exposed in the main notebook.
"""

import importlib.util
import json
import sys

# %% Imports and current-run inputs
from pathlib import Path

if "EXAMPLE" not in globals():
    EXAMPLE = Path(__file__).resolve().parent.parent
ROOT = EXAMPLE.parent.parent
sys.path.insert(0, str(ROOT))

# Imports follow repository-path and runtime setup.
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import pepflow as pf  # noqa: E402
from pepflow.constraint import PSDConstraint, ScalarConstraint  # noqa: E402
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis  # noqa: E402
from pepflow.operator import LinearOperatorTranspose  # noqa: E402
from pepflow.utils import Comparator  # noqa: E402

if "EXAMPLE" not in globals():
    EXAMPLE = Path(__file__).resolve().parent.parent
ROOT = EXAMPLE.parent.parent
HERE = EXAMPLE / "supplementary"
STATE = HERE / "b3_prior_N4"
NAME = "ogm_conjecture_4"
sys.dont_write_bytecode = True
b1 = json.loads((STATE / f"{NAME}_b1.json").read_text())
dense_data = json.loads((STATE / f"{NAME}_dense.json").read_text())
selected = json.loads((HERE / "b2_selected_capture.json").read_text())
N_int = int(selected["N_verify"])
params_sp = {k: sp.sympify(v) for k, v in json.loads(selected["params_json"]).items()}
setup_file = EXAMPLE / "ogm_conjecture4_setup.py"
assert selected["params_json"] == b1["params_json"]
assert N_int == b1["N_verify"]
assert selected["normalization"]["performance_metric"] == b1["performance_metric"]
assert selected["normalization"]["initial_condition"] == b1["initial_condition"]
assert Path(pf.__file__).resolve() == ROOT / "pepflow" / "__init__.py"
spec = importlib.util.spec_from_file_location("b2_verified_setup", setup_file)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load setup module: {setup_file}")

setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
ctx, pb, obj = setup.get_pep_setup(sp.S(N_int), params_sp)
pb.set_relaxed_constraints(selected["relaxed_constraints"])
# No new solve occurs: all multipliers and S belong to selected.solve_id.
ctx.set_as_current()
entries = [(c, "initial", None, None) for c in pb.init_conditions]
for owner in [*ctx.func_to_triplets, *ctx.oper_to_duplets]:
    if isinstance(owner, LinearOperatorTranspose):
        continue
    groups = ctx.get_constraint_data(owner)
    entries.extend(
        (c, "interpolation", str(owner), str(group))
        for group, constraints in groups.sc_dict.items()
        for c in constraints
    )
    entries.extend(
        (c, "interpolation", str(owner), str(group))
        for group, c in groups.psd_dict.items()
    )
assert len({c.name for c, *_ in entries}) == len(entries)
metadata = selected["constraint_metadata"]
named = selected["named_dual_values"]
assert set(metadata) == set(named) == {c.name for c, *_ in entries}
assert set(pb.relaxed_constraints).issubset(metadata)
for c, origin, owner, group in entries:
    scalar = isinstance(c, ScalarConstraint)
    assert scalar or isinstance(c, PSDConstraint)
    expected = dict(
        origin=origin,
        owner=owner,
        group=group,
        kind="scalar" if scalar else "psd",
        comparator=c.cmp.value,
        shape=[] if scalar else list(np.asarray(c.lhs - c.rhs).shape),
        relaxed=c.name in pb.relaxed_constraints,
    )
    assert metadata[c.name] == expected
    value = named[c.name]
    if expected["relaxed"]:
        assert value is None
    else:
        assert value is not None and np.all(np.isfinite(np.asarray(value, float)))
        assert list(np.asarray(value).shape) == expected["shape"]
basis = ctx.basis_vectors()
basis_labels = [str(v) for v in basis]
assert (
    basis_labels
    == selected["basis_vectors"]
    == selected["S_row_names"]
    == selected["S_col_names"]
)
assert [str(v) for v in ctx.basis_scalars()] == selected["basis_scalars"]
assert named["initial_condition"] == selected["tau_sol"]
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
print("Selected solve ID:", selected["certificate_provenance"]["solve_id"])
print(
    "Rebuilt inventory:",
    len(entries),
    "constraints;",
    len(pb.relaxed_constraints),
    "dropped",
)
print(
    "Dense objective:",
    dense_data["opt_value"],
    "selected objective:",
    selected["opt_value"],
)
print("Basis:", basis_labels)

# %% Selected S decomposition in original coordinates
S_array = np.asarray(selected["S_matrix"], float)
S_named = pf.MatrixWithNames(S_array, basis_labels, basis_labels)
# Other examples/reference formulas are prohibited by the user's clean-room clause.
# Current-run B1 had no proof decomposition. Use the generic reversed LDL routine.
D, ell = ldl_decompose_with_reversed_basis(S_named, basis, print_output=False)
D = np.asarray(D, float)
E = np.asarray([pm.eval_vector(v).coords for v in ell], float)
S_reconstructed = E.T @ D @ E
S_numeric = sum(
    (float(D[i, j]) * ell[i] * ell[j] for i, j in np.ndindex(D.shape)), pf.Scalar.zero()
)
S_eval = pm.eval_scalar(S_numeric)
numerical_decomposition = dict(
    method="reverse_ldl", D=D.tolist(), ell_coords=E.tolist(), basis_labels=basis_labels
)
print("S eigenvalues:", np.linalg.eigvalsh(S_array))
print("D diagonal:", np.diag(D))
print("Largest off-diagonal D entry:", np.max(np.abs(D - np.diag(np.diag(D)))))
print("Factors: ell_i = sum_j E[i,j] * basis[j]. No small factors are discarded.")
pf.pprint_labeled_matrix(
    E, [f"ell_{i}" for i in range(len(E))], basis_labels, precision=5
)
pf.pprint_labeled_matrix(S_reconstructed, basis_labels, basis_labels, precision=5)

# %% Full numerical coefficient identity and cone checks
tolerances = dict(
    identity_atol=1e-5,
    identity_rtol=0.0,
    reconstruction_atol=1e-4,
    reconstruction_rtol=1e-5,
    dual_tol=1e-6,
    psd_tol=1e-6,
    dense_opt_atol=1e-5,
    conjecture_relative_tolerance=1e-5,
)
weighted_constraints = pf.Scalar.zero()
scalar_inequality_values, matrix_inequality_eigenvalues = [], []
for c, *_ in entries:
    meta, value = metadata[c.name], named[c.name]
    if meta["relaxed"]:
        continue
    residual = c.lhs - c.rhs
    if c.cmp in (Comparator.GE, Comparator.SEQ):
        residual = -residual
    if meta["kind"] == "scalar":
        weighted_constraints += float(value) * (pf.Scalar.zero() + residual)
        if c.cmp != Comparator.EQ:
            scalar_inequality_values.append(float(value))
    else:
        dual = np.asarray(value, float)
        assert c.cmp != Comparator.EQ, (
            "Adapt pairing for any nonsymmetric matrix equality"
        )
        assert np.allclose(dual, dual.T, atol=tolerances["psd_tol"], rtol=0)
        weighted_constraints += sum(
            (float(dual[i, j]) * residual[j, i] for i, j in np.ndindex(dual.shape)),
            pf.Scalar.zero(),
        )
        matrix_inequality_eigenvalues.extend(np.linalg.eigvalsh((dual + dual.T) / 2))
diff = pb.performance_metric - selected["opt_value"] - weighted_constraints + S_numeric
checked = pm.eval_scalar(diff)
max_abs = lambda values: float(np.max(np.abs(np.asarray(values, float)), initial=0.0))  # noqa: E731 - retain the archived numerical helper
S_eigenvalues = np.linalg.eigvalsh((S_array + S_array.T) / 2)
candidate_bound = float(setup.conjectured_rate(N_int, params_sp["L"], params_sp["R"]))
residuals = dict(
    identity_gram_max_abs=max_abs(checked.inner_prod_coords),
    identity_func_max_abs=max_abs(checked.func_coords),
    identity_offset_abs=max_abs(checked.offset),
    S_reconstruction_max_abs=max_abs(S_reconstructed - S_array),
    S_expression_gram_max_abs=max_abs(S_eval.inner_prod_coords - S_array),
    S_expression_func_max_abs=max_abs(S_eval.func_coords),
    S_expression_offset_abs=max_abs(S_eval.offset),
    dense_relaxed_gap=abs(dense_data["opt_value"] - selected["opt_value"]),
    conjecture_relative_error=abs(selected["opt_value"] / candidate_bound - 1),
    minimum_scalar_inequality_dual=min(scalar_inequality_values, default=0.0),
    minimum_S_eigenvalue=float(S_eigenvalues.min()),
    minimum_matrix_inequality_eigenvalue=min(
        matrix_inequality_eigenvalues, default=0.0
    ),
)
passed = (
    selected["certificate_provenance"]["solver_status"] == "optimal"
    and np.all(np.isfinite(S_array))
    and np.allclose(S_array, S_array.T, atol=tolerances["psd_tol"], rtol=0)
    and all(
        residuals[key] <= tolerances["identity_atol"]
        for key in (
            "identity_gram_max_abs",
            "identity_func_max_abs",
            "identity_offset_abs",
            "S_expression_func_max_abs",
            "S_expression_offset_abs",
        )
    )
    and np.allclose(
        S_reconstructed,
        S_array,
        atol=tolerances["reconstruction_atol"],
        rtol=tolerances["reconstruction_rtol"],
    )
    and residuals["S_expression_gram_max_abs"] <= tolerances["reconstruction_atol"]
    and residuals["dense_relaxed_gap"] < tolerances["dense_opt_atol"]
    and residuals["conjecture_relative_error"]
    < tolerances["conjecture_relative_tolerance"]
    and residuals["minimum_scalar_inequality_dual"] >= -tolerances["dual_tol"]
    and residuals["minimum_S_eigenvalue"] >= -tolerances["psd_tol"]
    and residuals["minimum_matrix_inequality_eigenvalue"] >= -tolerances["psd_tol"]
)
numerical_checks = dict(tolerances=tolerances, residuals=residuals, passed=bool(passed))
print(json.dumps(numerical_checks, indent=2))
pf.pprint_labeled_matrix(
    np.asarray(checked.inner_prod_coords, float),
    basis_labels,
    basis_labels,
    precision=8,
)
pf.pprint_labeled_matrix(
    np.asarray(checked.func_coords, float).reshape(1, -1),
    ["function_residual"],
    selected["basis_scalars"],
    precision=8,
)
assert passed, "The numerical certificate is not ready for handoff"
print(
    "Numerical certificate verified. Analytic full-PEP and Lyapunov proofs remain unresolved."
)

# %% Save preliminary verification evidence; final handoff adds actual formula search
verification = dict(
    numerical_checks=numerical_checks, numerical_decomposition=numerical_decomposition
)
(HERE / "b2_verification.json").write_text(
    json.dumps(verification, indent=2, allow_nan=False) + "\n"
)
