"""Certificate replay and complete terminal-anchor partial-sum construction."""
import hashlib
from pathlib import Path

import numpy as np
import pepflow as pf
from certificate import certificate_id, inventory, verify_certificate


def replay_certificate(certificate, get_setup, root, dense_value):
    assert certificate_id(certificate) == certificate["certificate_id"]
    assert certificate["closed_form_search"]["completed"]
    assert certificate["certificate_provenance"]["pep_type"] == "primal"
    for relative, expected in certificate["certificate_provenance"]["source_hashes"].items():
        path = (Path(root) / relative).resolve()
        assert path.is_relative_to(Path(root).resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    assert Path(pf.__file__).resolve() == Path(root).resolve() / "supplementary/approved/pepflow/__init__.py"
    assert certificate["normalization"]["tau_name"] == certificate["tau_name"] == "initial_condition"
    assert abs(certificate["tau_sol"] - certificate["named_dual_values"]["initial_condition"]) <= 1e-6
    assert certificate["normalization"]["bound_value"] == certificate["opt_value"]
    checks, ctx, pm, checked = verify_certificate(certificate, get_setup, dense_value)
    assert checks["passed"]
    return checks, ctx, pm


def full_psd_piece(certificate, ctx, pm):
    """Keep the full numerical S as one boundary PSD block, without truncation."""
    basis = ctx.basis_vectors()
    matrix = np.asarray(certificate["S_matrix"], dtype=float)
    S_scalar = sum((float(matrix[i, j]) * basis[i] * basis[j]
                    for i, j in np.ndindex(matrix.shape)), pf.Scalar.zero())
    value = pm.eval_scalar(S_scalar)
    assert np.allclose(np.asarray(value.inner_prod_coords, dtype=float), matrix, atol=1e-5, rtol=0)
    assert np.allclose(value.func_coords, 0, atol=1e-5, rtol=0)
    assert abs(float(value.offset)) <= 1e-5
    assert np.linalg.eigvalsh((matrix + matrix.T) / 2).min() >= -1e-6
    return S_scalar, {"full_S": S_scalar}


def build_partial_sums(certificate, ctx, pb, pm, S_scalar, S_piece_terms):
    n = certificate["N_verify"]
    entries = inventory(ctx, pb)
    group_terms = {}
    for c, origin, _, _ in entries:
        d = certificate["named_dual_values"][c.name]
        if origin == "interpolation" and d is not None:
            assert c.cmp == pf.Comparator.LE and d >= -1e-6
            group_terms[c.name] = d * (c.lhs - c.rhs)
    term_assignment = {f"A monotone:x_{n},x_star": "boundary"}
    for k in range(n - 1):
        term_assignment[f"A monotone:x_{n},x_half_{k}"] = k
        term_assignment[f"A Lipschitz:x_{k},x_half_{k}"] = k
    term_assignment[f"A Lipschitz:x_{n-1},x_{n}"] = n - 1
    S_assignment = {"full_S": "boundary"}
    assert set(term_assignment) == set(group_terms)
    assert set(S_assignment) == set(S_piece_terms)
    lyap = [pf.Scalar.zero()]
    partial_sum = pf.Scalar.zero()
    increments = []
    for k in range(n):
        increment = sum((group_terms[name] for name, step in term_assignment.items() if step == k), pf.Scalar.zero())
        partial_sum += increment
        lyap.append(partial_sum)
        increments.append(increment)
    rank_tolerance = 1e-4
    rank_left, rank_right = 1, 1
    evaluated = [pm.eval_scalar(v) for v in lyap]
    matrices = [np.asarray(v.inner_prod_coords, dtype=float) for v in evaluated]
    singular_values = [np.linalg.svd(m, compute_uv=False).tolist() for m in matrices]
    ranks = [int(np.linalg.matrix_rank(m, tol=rank_tolerance)) for m in matrices]
    for k, rank in enumerate(ranks):
        print(f"rank V_{k}: {rank}")
        if k == 0:
            print()
    retained = ranks[rank_left:n + 1 - rank_right]
    print("Interior rank is constant at this N:", len(retained) >= 3 and len(set(retained)) == 1,
          "boundary exclusions:", (rank_left, rank_right))
    boundary_names = [name for name, step in term_assignment.items() if step == "boundary"]
    boundary_S = [name for name, step in S_assignment.items() if step == "boundary"]
    assert len(boundary_names) <= 1 and len(boundary_S) <= 1
    leftover = sum((group_terms[name] for name in boundary_names), pf.Scalar.zero())
    leftover -= sum((S_piece_terms[name] for name in boundary_S), pf.Scalar.zero())
    coverage = lyap[n] + leftover - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
    pieces_diff = sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar
    checked_residuals = {}
    expressions = [("coverage", coverage), ("S_pieces", pieces_diff)]
    expressions += [(f"increment_{k}", lyap[k+1] - lyap[k] - increments[k]) for k in range(n)]
    for label, expression in expressions:
        v = pm.eval_scalar(expression)
        residual = max(float(np.max(np.abs(np.asarray(v.inner_prod_coords, dtype=float)), initial=0)),
                       float(np.max(np.abs(np.asarray(v.func_coords, dtype=float)), initial=0)), abs(float(v.offset)))
        assert residual <= 1e-5
        checked_residuals[label] = residual
    # Each increment is a sum of nonnegative multipliers times residuals <= 0.
    # Thus the intended convention is V_{k+1} <= V_k, with V_0=0.
    observation = dict(N=n, certificate_id=certificate["certificate_id"],
        recipe_id="terminal_anchor_monotonicity_and_step_lipschitz__S_boundary",
        rank_profile=ranks, singular_values=singular_values,
        rank_convention=dict(tolerance=rank_tolerance, scaling="unscaled Gram matrix", coordinate_order="setup basis_vectors order"),
        rank_credible=not any(0.5e-4 <= s <= 2e-4 for row in singular_values for s in row),
        certificate_checked=True, grouping_checked=True, coverage_residuals=checked_residuals,
        lyap_inner_prod_coords=[m.tolist() for m in matrices],
        lyap_func_coords=[np.asarray(v.func_coords, dtype=float).tolist() for v in evaluated],
        lyap_offsets=[float(v.offset) for v in evaluated],
        grouping_coverage=dict(constraint_assignment=term_assignment, S_assignment=S_assignment,
            normalization_constraint="initial_condition", boundary_constraints=boundary_names,
            boundary_S=boundary_S, omitted_constraints=[], checked=True))
    return lyap, observation
