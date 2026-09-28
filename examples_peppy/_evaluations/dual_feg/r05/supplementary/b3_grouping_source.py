def group(certificate):
    ctx,pb,obj,pm,terms,S_scalar,residuals = recheck(certificate)
    N = certificate["N_verify"]
    term_assignment = {}
    group_terms = {n:v for n,v in terms.items() if n!="initial_condition"}
    for name in group_terms:
        if name == f"A monotone:x_{N},x_star":
            term_assignment[name] = "boundary"
        elif name.startswith("A monotone:"):
            term_assignment[name] = int(name.split(",y_")[1])
        elif name == f"A Lipschitz:x_{N-1},x_{N}":
            term_assignment[name] = N-1
        else:
            term_assignment[name] = int(name.split(",y_")[1])
    S_piece_terms = {"whole_S":S_scalar}
    S_assignment = {name: "boundary" for name in S_piece_terms}
    lyap = [pf.Scalar.zero()]
    partial_sum = pf.Scalar.zero()
    for k in range(N):
        partial_sum += sum((v for n,v in group_terms.items() if term_assignment[n] == k),pf.Scalar.zero())
        lyap.append(partial_sum)
    evaluated = [pm.eval_scalar(v) for v in lyap]
    matrices = [np.asarray(v.inner_prod_coords,dtype=float) for v in evaluated]
    svs = [np.linalg.svd(M,compute_uv=False) for M in matrices]
    ranks = [int(np.count_nonzero(s>1e-4)) for s in svs]
    boundary = sum((v for n,v in group_terms.items() if term_assignment[n]=="boundary"),pf.Scalar.zero())-S_scalar
    coverage = pm.eval_scalar(lyap[N]+boundary-(sum(group_terms.values(),pf.Scalar.zero())-S_scalar))
    coverage_res = [float(np.max(np.abs(coverage.inner_prod_coords))),float(np.max(np.abs(coverage.func_coords),initial=0)),abs(float(coverage.offset))]
    assert max(coverage_res)<=1e-5
    for k in range(N):
        inc=sum((v for n,v in group_terms.items() if term_assignment[n]==k),pf.Scalar.zero())
        chk=pm.eval_scalar(lyap[k+1]-lyap[k]-inc)
        assert np.max(np.abs(chk.inner_prod_coords))<=1e-5
        assert np.max(np.abs(chk.func_coords),initial=0)<=1e-5 and abs(float(chk.offset))<=1e-5
    assert sum(v=="boundary" for v in term_assignment.values())<=1
    report = {"N":N, "certificate_id":certificate["certificate_id"], "recipe_id":"forward_lip_mon_terminal_whole_S_boundary",
        "rank_profile":ranks, "singular_values":[s.tolist() for s in svs],
        "rank_convention":{"tolerance":1e-4,"scaling":"unscaled Gram matrix","coordinate_order":"setup basis, earlier iterates first"},
        "rank_credible":bool(all(not np.any((s>=5e-5)&(s<=2e-4)) for s in svs)),
        "certificate_checked":True,"grouping_checked":True,
        "identity_residuals":residuals,"coverage_residuals":coverage_res,
        "constraint_assignment":term_assignment,"S_assignment":S_assignment,
        "lyap_inner_prod_coords":[m.tolist() for m in matrices],
        "lyap_func_coords":[np.asarray(v.func_coords,dtype=float).tolist() for v in evaluated],
        "lyap_offsets":[float(v.offset) for v in evaluated]}
    return report

observation = group(certificate)
grouping_checked = observation["grouping_checked"]
ranks = observation["rank_profile"]
lyap = []
for coords, fcoords, offset in zip(observation["lyap_inner_prod_coords"], observation["lyap_func_coords"], observation["lyap_offsets"]):
    value = sum((float(coords[i][j])*ctx.basis_vectors()[i]*ctx.basis_vectors()[j] for i,j in np.ndindex(np.shape(coords))), pf.Scalar.zero())
    assert len(fcoords) == 0
    lyap.append(value + offset)
