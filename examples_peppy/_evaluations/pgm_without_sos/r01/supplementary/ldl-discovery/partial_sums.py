"""Verified saved-certificate partial sums for the chosen forward recipe."""
import hashlib
import json

import numpy as np
import pepflow as pf

from certificate import certificate_id, inventory, verify


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
    basis = ctx.basis_vectors()
    D = np.asarray(state["numerical_decomposition"]["D"])
    E = np.asarray(state["numerical_decomposition"]["ell_coords"])
    assert state["numerical_decomposition"]["basis_labels"] == state["basis_vectors"]
    ell = [sum((float(a)*v for a, v in zip(row, basis)), pf.Vector.zero()) for row in E]
    pieces, assignment = {}, {}
    index = 0
    N = state["N_verify"]
    while index < len(D):
        block = [index]
        if index+1 < len(D) and (D[index,index+1] != 0 or D[index+1,index] != 0):
            block.append(index+1)
        outside = [j for j in range(len(D)) if j not in block]
        assert np.max(np.abs(D[np.ix_(block, outside)]), initial=0) == 0
        assert np.max(np.abs(D[np.ix_(outside, block)]), initial=0) == 0
        piece = sum((float(D[i,j])*ell[i]*ell[j] for i in block for j in block), pf.Scalar.zero())
        label = f"ldl_{index}"
        pieces[label] = piece
        latest = 0
        for i in block:
            for coefficient, vector_label in zip(E[i], state["basis_vectors"]):
                if abs(coefficient) > 1e-6 and "x_" in vector_label and "star" not in vector_label:
                    latest = max(latest, int(vector_label.split("x_")[1].rstrip(")")))
        assignment[label] = max(0, min(N-1, latest-1))
        evaluated = pm.eval_scalar(piece)
        matrix = np.asarray(evaluated.inner_prod_coords, dtype=float)
        assert np.linalg.eigvalsh((matrix+matrix.T)/2).min() >= -1e-6
        assert np.max(np.abs(np.asarray(evaluated.func_coords, dtype=float)), initial=0) < 1e-5
        assert abs(float(evaluated.offset)) < 1e-5
        index += len(block)
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
        N=N, certificate_id=state["certificate_id"], recipe_id="forward_destination_reverse_ldl_latest_v1",
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
