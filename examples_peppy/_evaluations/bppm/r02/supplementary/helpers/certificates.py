"""Complete scalar-constraint certificate capture and replay for this attempt."""
import hashlib
import json
import uuid
from importlib.metadata import version
from typing import cast
import numpy as np
import sympy as sp
import pepflow as pf
from pepflow.utils import Comparator


def entries_for(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        assert not groups.psd_dict, "This setup uses scalar convex interpolation only"
        entries.extend((c, "interpolation", str(owner), str(group))
                       for group, constraints in groups.sc_dict.items() for c in constraints)
    assert not ctx.oper_to_duplets
    assert len({c.name for c, *_ in entries}) == len(entries)
    assert all(isinstance(c, pf.ScalarConstraint) for c, *_ in entries)
    return entries


def candidate_weights(N, alpha):
    weights = {"initial_condition": 1 / (alpha * N), f"h:x_star,x_{N}": 1 / (alpha * N)}
    for k in range(1, N + 1):
        weights[f"f:x_star,x_{k}"] = sp.Rational(1, N)
        weights[f"h:x_{k},x_{k-1}"] = k / (alpha * N)
        if k > 1:
            weights[f"f:x_{k-1},x_{k}"] = sp.Rational(k - 1, N)
            weights[f"h:x_{k-1},x_{k}"] = (k - 1) / (alpha * N)
    return weights


def max_abs(values):
    return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0.0))


def verify_certificate(ctx, pb, data):
    ctx.set_as_current()
    params = {k: sp.Rational(str(v)) for k, v in json.loads(data["params_json"]).items()}
    pm = pf.ExpressionManager(ctx, resolve_parameters=cast(dict[str, pf.NUMERICAL_TYPE], params))
    basis = ctx.basis_vectors()
    assert [str(v) for v in basis] == data["basis_vectors"]
    assert [str(v) for v in ctx.basis_scalars()] == data["basis_scalars"]
    entries = entries_for(ctx, pb)
    assert {c.name for c, *_ in entries} == set(data["named_dual_values"]) == set(data["constraint_metadata"])
    weighted = pf.Scalar.zero()
    inequalities = []
    for c, origin, owner, group in entries:
        meta = data["constraint_metadata"][c.name]
        assert meta == dict(origin=origin, owner=owner, group=group, kind="scalar",
                            comparator=c.cmp.value, shape=[], relaxed=c.name in data["relaxed_constraints"])
        value = data["named_dual_values"][c.name]
        if meta["relaxed"]:
            assert value is None
            continue
        assert value is not None and np.isfinite(value)
        residual = c.lhs - c.rhs
        if c.cmp == Comparator.GE:
            residual = -residual
        weighted += float(value) * (pf.Scalar.zero() + residual)
        if c.cmp != Comparator.EQ:
            inequalities.append(value)
    S = np.asarray(data["S_matrix"], dtype=float)
    D = np.asarray(data["numerical_decomposition"]["D"], dtype=float)
    E = np.asarray(data["numerical_decomposition"]["ell_coords"], dtype=float)
    reconstructed = E.T @ D @ E
    S_scalar = sum((float(S[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S.shape)), pf.Scalar.zero())
    checked = pm.eval_scalar(pb.performance_metric - float(data["opt_value"]) - weighted + S_scalar)
    residuals = dict(identity_gram_max_abs=max_abs(checked.inner_prod_coords),
                     identity_func_max_abs=max_abs(checked.func_coords), identity_offset_abs=max_abs(checked.offset),
                     S_reconstruction_max_abs=max_abs(reconstructed-S),
                     dense_relaxed_gap=abs(data["dense_opt_value"]-data["opt_value"]),
                     minimum_scalar_inequality_dual=min(inequalities, default=0.0),
                     minimum_S_eigenvalue=float(np.linalg.eigvalsh((S+S.T)/2).min()),
                     minimum_matrix_inequality_eigenvalue=0.0,
                     conjectured_rate_error=abs(data["opt_value"]-float(params["R"]/(params["alpha"]*data["N"]))))
    passed = (data["certificate_provenance"]["solver_status"] == "optimal"
              and all(residuals[k] <= 1e-5 for k in ("identity_gram_max_abs", "identity_func_max_abs", "identity_offset_abs"))
              and np.allclose(S, S.T, atol=1e-6, rtol=0)
              and np.allclose(S, reconstructed, atol=1e-4, rtol=1e-5)
              and residuals["dense_relaxed_gap"] < 1e-5
              and residuals["conjectured_rate_error"] <= 1e-5
              and residuals["minimum_scalar_inequality_dual"] >= -1e-6
              and residuals["minimum_S_eigenvalue"] >= -1e-6)
    assert passed, residuals
    return {"passed": bool(passed), "residuals": residuals,
            "tolerances": {"identity_atol":1e-5,"identity_rtol":0,"reconstruction_atol":1e-4,
                           "reconstruction_rtol":1e-5,"dual_tol":1e-6,"psd_tol":1e-6,"dense_opt_atol":1e-5}}, checked


CERTIFICATE_KEYS = ("N_verify", "params_json", "relaxed_constraints", "S_matrix", "S_row_names", "S_col_names",
                    "basis_vectors", "basis_scalars", "opt_value", "tau_sol", "tau_name", "named_dual_values",
                    "constraint_metadata", "normalization", "certificate_provenance", "numerical_checks", "numerical_decomposition")


def certificate_id(data):
    return hashlib.sha256(json.dumps({key:data[key] for key in CERTIFICATE_KEYS}, sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def capture(ctx, pb, result, attempts, b1, dense_value, source_hashes):
    S = result.get_gram_dual_matrix()
    eigenvalues, eigenvectors = np.linalg.eigh(S.matrix)
    metadata, values = {}, {}
    for c, origin, owner, group in entries_for(ctx, pb):
        dropped = c.name in pb.relaxed_constraints
        value = result.get_dual_value(c.name)
        assert value is not None or dropped
        metadata[c.name] = dict(origin=origin, owner=owner, group=group, kind="scalar",
                                comparator=c.cmp.value, shape=[], relaxed=dropped)
        values[c.name] = None if dropped else float(value)
    data = {**b1, "N": b1["N_verify"], "opt_value":float(result.opt_value), "dense_opt_value":float(dense_value),
            "tau_sol":float(result.get_dual_value("initial_condition")), "tau_name":"initial_condition",
            "relaxed_constraints":list(pb.relaxed_constraints), "S_matrix":S.matrix.tolist(),
            "S_row_names":list(S.row_names), "S_col_names":list(S.col_names),
            "basis_vectors":[str(v) for v in ctx.basis_vectors()], "basis_scalars":[str(v) for v in ctx.basis_scalars()],
            "named_dual_values":values, "constraint_metadata":metadata,
            "normalization":{"tau_name":"initial_condition", "initial_condition":b1["initial_condition"],
                             "performance_metric":b1["performance_metric"], "bound_value":float(result.opt_value),
                             "bound_formula":b1["conjectured_rate"]},
            "certificate_provenance":{"solve_id":str(uuid.uuid4()), "pep_type":"primal", "solver_status":str(result.solver_status),
                                      "source_hashes":source_hashes, "solver":{"api":"CVXPrimalSolver.build_problem",
                                      "cvxpy_version":version("cvxpy"), "attempts":attempts}},
            "numerical_decomposition":{"method":"direct", "description":"symmetric eigendecomposition; no eigenvalues discarded",
                                       "D":np.diag(eigenvalues).tolist(), "ell_coords":eigenvectors.T.tolist(),
                                       "basis_labels":[str(v) for v in ctx.basis_vectors()]}}
    checks, _ = verify_certificate(ctx, pb, data)
    data["numerical_checks"] = checks
    data["certificate_id"] = certificate_id(data)
    all_groups = {}
    for owner in ctx.func_to_triplets:
        matrix = result.get_scalar_constraint_dual_value_in_numpy(owner)
        if isinstance(matrix, dict):
            all_groups[str(owner)] = {name:{"matrix":m.matrix.tolist(),"row_names":m.row_names,"col_names":m.col_names} for name,m in matrix.items()}
        else:
            all_groups[str(owner)] = {"convex":{"matrix":matrix.matrix.tolist(),"row_names":matrix.row_names,"col_names":matrix.col_names}}
    data["all_owner_lambda_groups"] = all_groups
    primary = next(iter(all_groups["f"].values()))
    data.update(lambda_matrix=primary["matrix"],lambda_row_names=primary["row_names"],lambda_col_names=primary["col_names"])
    return data

