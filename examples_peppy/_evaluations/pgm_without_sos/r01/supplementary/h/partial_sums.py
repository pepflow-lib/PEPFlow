"""Verified saved-certificate partial sums for the chosen forward recipe."""
import hashlib
import json

import numpy as np
import pepflow as pf

from certificate import certificate_id, inventory, verify
from analytic import finite_pieces


def rebuild_check(root, state, get_pep_setup):
    assert certificate_id(state) == state["certificate_id"]
    for relative, expected in state["certificate_provenance"]["source_hashes"].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
    assert state["closed_form_search"]["completed"]
    params = json.loads(state["params_json"])
    ctx, pb, obj = get_pep_setup(state["N_verify"], params)
    pb.set_relaxed_constraints(state["relaxed_constraints"])
    checks, _, _ = verify(ctx, pb, params, state)
    assert checks["passed"]
    assert state["S_row_names"] == state["basis_vectors"] == state["S_col_names"]
    assert state["normalization"]["bound_value"] == state["opt_value"]
    assert state["normalization"]["tau_name"] == state["tau_name"] == "initial_condition"
    assert state["named_dual_values"]["initial_condition"] == state["tau_sol"]
    assert state["normalization"]["initial_condition"] == "||x_0-x_star||^2 <= R^2"
    assert state["normalization"]["performance_metric"] == "h(x_N)-h(x_star)"
    return ctx, pb, obj, checks


def build_pieces(ctx, state, pm):
    f = next(owner for owner in ctx.func_to_triplets if str(owner) == "f")
    g = next(owner for owner in ctx.func_to_triplets if str(owner) == "g")
    pieces, assignment = finite_pieces(ctx, f, g, f.L, state["N_verify"])
    basis = ctx.basis_vectors()
    raw = {name: pm.eval_scalar(piece).inner_prod_coords.astype(float)
           for name, piece in pieces.items()}
    analytic_S = sum(raw.values())
    numerical_S = np.asarray(state["S_matrix"])
    eigen_a, U = np.linalg.eigh((analytic_S+analytic_S.T)/2)
    active = eigen_a > 1e-10
    projector = U[:,active]@U[:,active].T
    inverse_root = (U[:,active]/np.sqrt(eigen_a[active]))@U[:,active].T
    assert np.max(np.abs((U[:,active]*eigen_a[active])@U[:,active].T-analytic_S)) < 1e-10
    eigen_s, W = np.linalg.eigh((numerical_S+numerical_S.T)/2)
    assert eigen_s.min() >= -1e-6
    root_s = (W*np.sqrt(np.maximum(eigen_s,0)))@W.T
    transform = root_s@inverse_root
    corrected = {name: transform@matrix@transform.T for name,matrix in raw.items()}
    corrected["numerical_nullspace_remainder"] = root_s@(np.eye(len(basis))-projector)@root_s.T
    assignment["numerical_nullspace_remainder"] = state["N_verify"]-1
    pieces = {
        name: sum((float(matrix[i,j])*basis[i]*basis[j]
                   for i,j in np.ndindex(matrix.shape)), pf.Scalar.zero())
        for name,matrix in corrected.items()}
    for piece in pieces.values():
        evaluated = pm.eval_scalar(piece)
        matrix = np.asarray(evaluated.inner_prod_coords, dtype=float)
        assert np.linalg.eigvalsh((matrix+matrix.T)/2).min() >= -1e-6
        assert np.max(np.abs(np.asarray(evaluated.func_coords, dtype=float)), initial=0) < 1e-5
        assert abs(float(evaluated.offset)) < 1e-5
    reconstructed = pm.eval_scalar(sum(pieces.values(), pf.Scalar.zero()))
    assert np.allclose(reconstructed.inner_prod_coords.astype(float), state["S_matrix"], atol=1e-5, rtol=0)
    return pieces, assignment


def construct(ctx, pb, state, verbose=False):
    ctx.set_as_current()
    params = json.loads(state["params_json"])
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    N = state["N_verify"]
    pieces, S_assignment = build_pieces(ctx, state, pm)
    terms, assignment = {}, {}
    for c, origin, _, _ in inventory(ctx, pb):
        value = state["named_dual_values"][c.name]
        if origin == "initial":
            assert c.name == "initial_condition"
            continue
        if value is None:
            continue
        assert value >= -1e-6
        assert c.cmp in (pf.Comparator.LE, pf.Comparator.GE)
        residual = c.lhs-c.rhs
        if c.cmp == pf.Comparator.GE:
            residual = -residual
        terms[c.name] = value*residual
        destination = int(c.name.split(",")[1][2:])
        assignment[c.name] = max(0, min(N-1, destination-1))
    lyap = [pf.Scalar.zero()]
    partial_sum = pf.Scalar.zero()
    for k in range(N):
        increment = sum((term for name, term in terms.items() if assignment[name] == k), pf.Scalar.zero())
        increment -= sum((piece for name, piece in pieces.items() if S_assignment[name] == k), pf.Scalar.zero())
        partial_sum += increment
        lyap.append(partial_sum)
    values = [pm.eval_scalar(value) for value in lyap]
    matrices = [np.asarray(value.inner_prod_coords, dtype=float) for value in values]
    singular = [np.linalg.svd(matrix, compute_uv=False) for matrix in matrices]
    ranks = [int(np.sum(sv > 1e-4)) for sv in singular]
    if verbose:
        for k, rank in enumerate(ranks):
            print(f"rank V_{k}: {rank}")
            if k == 0:
                print()
        print("Interior rank is constant at this N:", len(ranks[1:-1]) >= 3 and len(set(ranks[1:-1])) == 1,
              "boundary exclusions:", (1, 1))
    def full_error(expression):
        v = pm.eval_scalar(expression)
        return max(float(np.max(np.abs(np.asarray(v.inner_prod_coords, dtype=float)), initial=0)),
                   float(np.max(np.abs(np.asarray(v.func_coords, dtype=float)), initial=0)),
                   abs(float(v.offset)))
    S_scalar = sum((float(a)*u*v for row, u in zip(state["S_matrix"], ctx.basis_vectors())
                    for a, v in zip(row, ctx.basis_vectors())), pf.Scalar.zero())
    coverage = full_error(lyap[-1]-(sum(terms.values(), pf.Scalar.zero())-S_scalar))
    increments = []
    for k in range(N):
        increment = sum((term for name, term in terms.items() if assignment[name] == k), pf.Scalar.zero())
        increment -= sum((piece for name, piece in pieces.items() if S_assignment[name] == k), pf.Scalar.zero())
        increments.append(full_error(lyap[k+1]-lyap[k]-increment))
    boundary = full_error(lyap[-1]-(pb.performance_metric-
        state["tau_sol"]*(ctx["x_0"]-ctx["x_star"])**2))
    assert max(coverage, boundary, *increments) < 1e-5
    record = dict(
        N=N, certificate_id=state["certificate_id"], recipe_id="forward_destination_analytic_psd_congruence_v3",
        rank_profile=ranks, singular_values=[sv.tolist() for sv in singular],
        rank_convention={"tolerance": 1e-4, "scaling": "absolute_unscaled",
                         "coordinate_order": "original_framework_basis_earlier_iterates_first"},
        rank_credible=all(not np.any((sv > 5e-5) & (sv < 2e-4)) for sv in singular),
        certificate_checked=True, grouping_checked=True, coverage_max_abs=coverage,
        boundary_max_abs=boundary, increment_max_abs=max(increments),
        constraint_assignment=assignment, S_assignment=S_assignment,
        boundary_constraints=[], boundary_S=[], omitted_constraints=[],
        sign_convention="V(k+1)-V(k)=sum(nonnegative_dual * residual_le_0)-sum(PSD_pieces), hence nonincreasing",
        normalization_constraint="initial_condition",
        lyap_inner_prod_coords=[v.inner_prod_coords.astype(float).tolist() for v in values],
        lyap_func_coords=[v.func_coords.astype(float).tolist() for v in values],
        lyap_offsets=[float(v.offset) for v in values])
    return lyap, pieces, terms, record

