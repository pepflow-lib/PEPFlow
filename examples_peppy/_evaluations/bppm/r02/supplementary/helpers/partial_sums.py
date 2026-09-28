"""Saved-certificate partial sums; no solve is performed here."""
import hashlib
from pathlib import Path
import numpy as np
import sympy as sp
import pepflow as pf
from certificates import certificate_id, entries_for, verify_certificate, max_abs


def replay_certificate(ctx, pb, certificate, attempt):
    assert certificate_id(certificate) == certificate["certificate_id"]
    assert certificate["closed_form_search"]["completed"]
    for rel, expected in certificate["certificate_provenance"]["source_hashes"].items():
        path = (Path(attempt) / rel).resolve()
        assert path.is_relative_to(Path(attempt).resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    assert Path(pf.__file__).resolve() == Path(attempt) / "supplementary/approved/pepflow/__init__.py"
    assert certificate["normalization"]["bound_value"] == certificate["opt_value"]
    assert certificate["normalization"]["initial_condition"] == "D_h(x_star,x_0) <= R"
    assert certificate["normalization"]["performance_metric"] == "f(x_N) - f(x_star)"
    assert certificate["tau_sol"] == certificate["named_dual_values"]["initial_condition"]
    assert certificate["S_row_names"] == certificate["basis_vectors"] == certificate["S_col_names"]
    assert set(pb.relaxed_constraints) == set(certificate["relaxed_constraints"])
    checks, _ = verify_certificate(ctx, pb, certificate)
    return checks


def decompose_saved_S(ctx, certificate):
    basis = ctx.basis_vectors()
    S_array = np.asarray(certificate["S_matrix"], dtype=float)
    D = np.asarray(certificate["numerical_decomposition"]["D"], dtype=float)
    E = np.asarray(certificate["numerical_decomposition"]["ell_coords"], dtype=float)
    assert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
    S_scalar = sum((float(S_array[i,j]) * basis[i] * basis[j] for i,j in np.ndindex(S_array.shape)), pf.Scalar.zero())
    # Retain the complete small PSD block as one terminal piece, not zero.
    S_piece_terms = {"complete_S": S_scalar}
    assert np.linalg.eigvalsh((S_array+S_array.T)/2).min() >= -1e-6
    return S_scalar, S_piece_terms


def construct_partial_sums(ctx, pb, certificate):
    ctx.set_as_current()
    pm = pf.ExpressionManager(ctx, resolve_parameters={"alpha":sp.Integer(1), "R":sp.Integer(1)})
    N_int = certificate["N_verify"]
    rank_tolerance = 1e-4
    rank_left, rank_right = 1, 1
    weighted_terms = {}
    for c,*_ in entries_for(ctx,pb):
        value = certificate["named_dual_values"][c.name]
        if value is not None:
            assert c.cmp.name == "LE"
            assert value >= -1e-6
            weighted_terms[c.name] = float(value)*(pf.Scalar.zero()+c.lhs-c.rhs)
    group_terms = {name:term for name,term in weighted_terms.items() if name != "initial_condition"}
    term_assignment = {}
    for name in group_terms:
        if name == f"h:x_star,x_{N_int}":
            term_assignment[name] = "boundary"
        else:
            pair = name.split(":")[1].split(",")
            indices = [int(p[2:]) for p in pair if p != "x_star"]
            term_assignment[name] = max(indices)-1
    S_scalar, S_piece_terms = decompose_saved_S(ctx,certificate)
    S_assignment = {"complete_S":"boundary"}
    assert set(term_assignment) == set(group_terms)
    assert all(step=="boundary" or (isinstance(step, int) and 0<=step<N_int) for step in term_assignment.values())
    # Each increment is a sum of nonpositive convex interpolation residuals
    # with nonnegative multipliers. Thus this V is nonincreasing.
    lyap = [pf.Scalar.zero()]
    partial_sum = pf.Scalar.zero()
    for step in range(N_int):
        partial_sum += sum((group_terms[name] for name,target in term_assignment.items() if target==step),pf.Scalar.zero())
        partial_sum -= sum((S_piece_terms[name] for name,target in S_assignment.items() if target==step),pf.Scalar.zero())
        lyap.append(partial_sum)
    ranks, singular_values = [], []
    evaluated = [pm.eval_scalar(V) for V in lyap]
    for k,V in enumerate(evaluated):
        matrix = np.asarray(V.inner_prod_coords,dtype=float)
        rank = int(np.linalg.matrix_rank(matrix,tol=rank_tolerance))
        ranks.append(rank)
        singular_values.append(np.linalg.svd(matrix,compute_uv=False).tolist())
        print(f"rank V_{k}: {rank}")
        if k==0:
            print()
    retained = ranks[rank_left:N_int+1-rank_right]
    print("Interior rank is constant at this N:",len(retained)>=3 and len(set(retained))==1,
          "boundary exclusions:",(rank_left,rank_right))
    boundary_names = [name for name,step in term_assignment.items() if step=="boundary"]
    boundary_S = [name for name,step in S_assignment.items() if step=="boundary"]
    assert len(boundary_names)<=1 and len(boundary_S)<=1
    leftover = sum((group_terms[n] for n in boundary_names),pf.Scalar.zero()) - sum((S_piece_terms[n] for n in boundary_S),pf.Scalar.zero())
    coverage = lyap[N_int] + leftover - (sum(group_terms.values(),pf.Scalar.zero())-S_scalar)
    coordinate_errors = {}
    expressions = {"coverage":coverage,"S_pieces":sum(S_piece_terms.values(),pf.Scalar.zero())-S_scalar}
    for k in range(N_int):
        increment = sum((group_terms[name] for name,step in term_assignment.items() if step==k),pf.Scalar.zero())
        expressions[f"increment_{k}"] = lyap[k+1]-lyap[k]-increment
    for name,expr in expressions.items():
        value=pm.eval_scalar(expr)
        coordinate_errors[name] = {"gram":max_abs(value.inner_prod_coords),"function":max_abs(value.func_coords),"offset":max_abs(value.offset)}
        assert max(coordinate_errors[name].values()) <= 1e-5
    for piece in S_piece_terms.values():
        value=pm.eval_scalar(piece)
        assert max_abs(value.func_coords)<=1e-5 and max_abs(value.offset)<=1e-5
        assert np.linalg.eigvalsh(np.asarray(value.inner_prod_coords,dtype=float)).min() >= -1e-6
    # Inspect separation from the fixed absolute singular-value threshold.
    significant = [s for row in singular_values for s in row if s>rank_tolerance]
    negligible = [s for row in singular_values for s in row if s<=rank_tolerance]
    credible = (not significant or min(significant)>10*rank_tolerance) and (not negligible or max(negligible)<rank_tolerance/10)
    observation = {"N":N_int,"certificate_id":certificate["certificate_id"],"recipe_id":"adjacent_max_index_terminal_h_and_whole_S",
                   "rank_profile":ranks,"rank_convention":{"tolerance":rank_tolerance,"scaling":"unscaled Gram coordinate matrix","coordinate_order":"setup basis order"},
                   "rank_credible":bool(credible),"certificate_checked":True,"grouping_checked":True,
                   "singular_values":singular_values,"coordinate_errors":coordinate_errors,
                   "constraint_assignment":term_assignment,"S_assignment":S_assignment,"boundary_constraints":boundary_names,"boundary_S":boundary_S,
                   "minimum_significant_singular_value":min(significant,default=0),"maximum_negligible_singular_value":max(negligible,default=0),
                   "lyap_inner_prod_coords":[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in evaluated],
                   "lyap_func_coords":[np.asarray(v.func_coords,dtype=float).tolist() for v in evaluated],"lyap_offsets":[float(v.offset) for v in evaluated]}
    return lyap, observation

