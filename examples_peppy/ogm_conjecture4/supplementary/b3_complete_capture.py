"""Finalize and revalidate a horizon-specific raw capture for rank exploration.

No solve occurs here. Each raw capture already contains all duals from one solve.
"""

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
EXAMPLE = HERE.parent
REPO_ROOT = EXAMPLE.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.dont_write_bytecode = True
# Imports follow repository-path and runtime setup.
import numpy as np  # noqa: E402

import pepflow as pf  # noqa: E402
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis  # noqa: E402


def complete(raw_path):
    original_b2 = HERE / "b3_prior_N4" / "ogm_conjecture_4_b2.json"
    b2 = json.loads(original_b2.read_text())
    raw = json.loads(raw_path.read_text())
    certificate: dict[str, Any] = {**copy.deepcopy(b2), **raw}
    n = raw["N_verify"]
    # The saved JSON and exec-populated namespace contain different object types.
    namespace: dict[str, Any] = dict(
        __file__=str(HERE / "b3_load.py"), EXAMPLE=EXAMPLE, certificate=certificate
    )
    exec(
        compile((HERE / "b3_load.py").read_text(), str(HERE / "b3_load.py"), "exec"),
        namespace,
    )
    ctx, pb, obj = (namespace[k] for k in ("ctx", "pb", "obj"))
    params_sp = namespace["params_sp"]
    basis = list(ctx.basis_vectors())
    labels = [repr(v) for v in basis]
    assert labels == raw["basis_vectors"] == raw["S_row_names"] == raw["S_col_names"]
    pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
    S = np.asarray(raw["S_matrix"], float)
    D, ell = ldl_decompose_with_reversed_basis(
        pf.MatrixWithNames(S, labels, labels), basis, print_output=False
    )
    E = np.asarray([pm.eval_vector(v).coords for v in ell], float)
    certificate["numerical_decomposition"] = dict(
        method="reverse_ldl", D=D.tolist(), ell_coords=E.tolist(), basis_labels=labels
    )
    certificate["S_decomp_type"] = "ldl"
    terms = [(c, "initial") for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        terms.extend(
            (c, "interpolation") for c in owner.get_interpolation_constraints(ctx)
        )
    assert not ctx.oper_to_duplets, "Adapt inventory to operators before use"
    weighted = pf.Scalar.zero()
    for c, origin in terms:
        value = raw["named_dual_values"][c.name]
        if value is None:
            assert c.name in raw["relaxed_constraints"]
            continue
        assert c.cmp.name == "LE" and value >= -1e-6
        weighted += float(value) * (c.lhs - c.rhs)
    S_scalar = sum(
        (float(S[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S.shape)),
        pf.Scalar.zero(),
    )
    checked = pm.eval_scalar(
        pb.performance_metric - raw["opt_value"] - weighted + S_scalar
    )
    max_abs = lambda v: float(np.max(np.abs(np.asarray(v, float)), initial=0.0))  # noqa: E731 - retain the archived numerical helper
    b1 = json.loads((HERE / "b3_prior_N4" / "ogm_conjecture_4_b1.json").read_text())
    dense_value = raw.get("dense_reference_value")
    if dense_value is None:
        dense_value = next(r["opt_value"] for r in b1["sweep_results"] if r["N"] == n)
    target = float(namespace["mod"].conjectured_rate(n))
    residuals = dict(
        identity_gram_max_abs=max_abs(checked.inner_prod_coords),
        identity_func_max_abs=max_abs(checked.func_coords),
        identity_offset_abs=max_abs(checked.offset),
        S_reconstruction_max_abs=max_abs(E.T @ D @ E - S),
        dense_relaxed_gap=abs(dense_value - raw["opt_value"]),
        conjecture_relative_error=abs(raw["opt_value"] / target - 1),
        minimum_scalar_inequality_dual=min(
            v for v in raw["named_dual_values"].values() if v is not None
        ),
        minimum_S_eigenvalue=float(np.linalg.eigvalsh(S).min()),
        minimum_matrix_inequality_eigenvalue=0.0,
    )
    tolerances = copy.deepcopy(b2["numerical_checks"]["tolerances"])
    assert (
        max(
            residuals[k]
            for k in (
                "identity_gram_max_abs",
                "identity_func_max_abs",
                "identity_offset_abs",
            )
        )
        <= tolerances["identity_atol"]
    )
    assert residuals["S_reconstruction_max_abs"] <= tolerances["reconstruction_atol"]
    assert residuals["minimum_S_eigenvalue"] >= -tolerances["psd_tol"]
    assert residuals["dense_relaxed_gap"] < tolerances["dense_opt_atol"]
    assert (
        residuals["conjecture_relative_error"]
        < tolerances["conjecture_relative_tolerance"]
    )
    certificate["numerical_checks"] = dict(
        tolerances=tolerances, residuals=residuals, passed=True
    )
    certificate["numerical_certificate_verified"] = True
    certificate["analytic_full_pep_verified"] = certificate[
        "lyapunov_proof_verified"
    ] = False
    certificate["closed_form_search"] = copy.deepcopy(b2["closed_form_search"])
    certificate["closed_form_search"]["source_N"] = b2["N_verify"]
    certificate["closed_form_search"]["comparison_scope"] = (
        "Inherited candidate fit errors and 'selected' wording refer only to the original N=4 sample. They do not assert a fit to this new certificate."
    )
    certificate["closed_form_search"]["candidates_compared_to_current_certificate"] = (
        False
    )
    certificate["closed_form_search"]["reused_from_certificate"] = b2["certificate_id"]
    certificate["closed_form_search"]["reuse_note"] = (
        "Same algorithm/normalization/sparse support; numerical certificate independently revalidated at this horizon. Existing formulas remain candidates."
    )
    certificate["certificate_provenance"]["source_hashes"][
        Path(__file__).relative_to(REPO_ROOT).as_posix()
    ] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    keys = (
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
    certificate["certificate_id"] = hashlib.sha256(
        json.dumps(
            {k: certificate[k] for k in keys},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    namespace["certificate"] = certificate
    exec(
        compile(
            (HERE / "b3_certificate_check.py").read_text(),
            str(HERE / "b3_certificate_check.py"),
            "exec",
        ),
        namespace,
    )
    assert namespace["certificate_checked"]
    destination = HERE / f"b3_N{n}_certificate.json"
    destination.write_text(json.dumps(certificate, indent=2, allow_nan=False) + "\n")
    print(
        "Complete sample:",
        destination.name,
        "certificate",
        certificate["certificate_id"],
        "checks",
        residuals,
    )


if __name__ == "__main__":
    n_argument = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    complete(HERE / f"b3_N{n_argument}_capture.json")
