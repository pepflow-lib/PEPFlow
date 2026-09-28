"""PSD square transport for the same saved numerical slack."""
import numpy as np
import pepflow as pf
import sympy as sp

from certificates import inventory, residual, maxabs
from grouping import replay


def transport_pieces(ctx, certificate, pm):
    """Align the supplied factor coordinates with the actual numerical S."""
    basis=ctx.basis_vectors()
    S=np.asarray(certificate["S_matrix"],dtype=float)
    E=np.asarray(certificate["numerical_decomposition"]["ell_coords"],dtype=float)
    D=np.asarray(certificate["numerical_decomposition"]["D"],dtype=float)
    B=E.T@np.diag(np.sqrt(np.diag(D)))
    A=B@B.T
    av,au=np.linalg.eigh(A)
    keep=av>1e-10
    # This cutoff constructs the transport only; it does not alter rank/check tolerances.
    Ai=(au[:,keep]/np.sqrt(av[keep]))@au[:,keep].T
    sv,su=np.linalg.eigh(S)
    assert sv.min()>=0
    Sh=(su*np.sqrt(sv))@su.T
    Bnew=Sh@Ai@B
    Bnull=Sh@au[:,~keep]
    assert np.max(abs(Bnew@Bnew.T+Bnull@Bnull.T-S))<1e-10
    pieces={}
    assignments={}
    for column in range(Bnew.shape[1]):
        i,family=certificate["numerical_decomposition"]["piece_labels"][column]
        vector=sum((float(coef)*v for coef,v in zip(Bnew[:,column],basis)),pf.Vector.zero())
        name=f"S{i}_{family}"
        pieces[name]=vector**2
        assignments[name]=i-1
    pieces["transport_null"]=sum((
        sum((float(coef)*v for coef,v in zip(Bnull[:,j],basis)),pf.Vector.zero())**2
        for j in range(Bnull.shape[1])),pf.Scalar.zero())
    assignments["transport_null"]=certificate["N_verify"]-1
    return pieces,assignments



def construct(certificate, verbose=True):
    ctx,pb,checks=replay(certificate)
    n=certificate["N_verify"]
    pm=pf.ExpressionManager(ctx,resolve_parameters={"L":sp.S.One,"R":sp.S.One})
    group_terms={}
    term_assignment={}
    for c,origin,_,_ in inventory(ctx,pb):
        v=certificate["named_dual_values"][c.name]
        if origin=="initial" or v is None:
            continue
        group_terms[c.name]=v*residual(c)
        _,pair=c.name.split(":")
        a,b=pair.split(",")
        j=int(b[2:])
        assert a=="x_star" or int(a[2:])+1==j
        term_assignment[c.name]=j-1
    pieces,S_assignment=transport_pieces(ctx,certificate,pm)
    total_S=sum(pieces.values(),pf.Scalar.zero())
    basis=ctx.basis_vectors()
    mat=np.array(certificate["S_matrix"])
    S_scalar=sum((float(mat[i,j])*basis[i]*basis[j] for i,j in np.ndindex(mat.shape)),
                 pf.Scalar.zero())
    piece_diff=pm.eval_scalar(total_S-S_scalar)
    piece_residual=max(maxabs(piece_diff.inner_prod_coords),maxabs(piece_diff.func_coords),maxabs(piece_diff.offset))
    assert piece_residual<=1e-5
    for piece in pieces.values():
        q=pm.eval_scalar(piece)
        assert maxabs(q.func_coords)==0 and maxabs(q.offset)==0
        assert np.linalg.eigvalsh(np.array(q.inner_prod_coords,dtype=float)).min()>=-1e-6
    lyap=[pf.Scalar.zero()]
    partial_sum=sum((t for name,t in group_terms.items() if term_assignment[name]==-1),pf.Scalar.zero())
    for k in range(n):
        increment=sum((t for name,t in group_terms.items() if term_assignment[name]==k),pf.Scalar.zero())
        increment-=sum((t for name,t in pieces.items() if S_assignment[name]==k),pf.Scalar.zero())
        partial_sum+=increment
        lyap.append(partial_sum)
    ranks=[]
    singular_values=[]
    coords=[]
    for k,V in enumerate(lyap):
        q=pm.eval_scalar(V)
        matrix=np.array(q.inner_prod_coords,dtype=float)
        sv=np.linalg.svd(matrix,compute_uv=False)
        rank=int(np.sum(sv>1e-4))
        ranks.append(rank)
        singular_values.append(sv.tolist())
        coords.append(dict(gram=matrix.tolist(),func=np.array(q.func_coords,dtype=float).tolist(),offset=float(q.offset)))
        if verbose:
            print(f"rank V_{k}: {rank}")
            if k==0:
                print()
    if verbose:
        print("Interior rank is constant at this N:",len(set(ranks[1:-1]))==1 and n-1>=3,
              "boundary exclusions:",(1,1))
    coverage=pm.eval_scalar(lyap[-1]-(sum(group_terms.values(),pf.Scalar.zero())-S_scalar))
    coverage_residual=max(maxabs(coverage.inner_prod_coords),maxabs(coverage.func_coords),maxabs(coverage.offset))
    assert coverage_residual<=1e-5
    step_residuals=[]
    for k in range(n):
        included={-1,0} if k==0 else {k}
        inc=sum((t for name,t in group_terms.items() if term_assignment[name] in included),pf.Scalar.zero())
        inc-=sum((t for name,t in pieces.items() if S_assignment[name] in included),pf.Scalar.zero())
        q=pm.eval_scalar(lyap[k+1]-lyap[k]-inc)
        step_residuals.append(max(maxabs(q.inner_prod_coords),maxabs(q.func_coords),maxabs(q.offset)))
    assert max(step_residuals)<=1e-5
    sample=dict(N=n,certificate_id=certificate["certificate_id"],recipe_id="forward-star-transported-SOS",
       rank_profile=ranks,singular_values=singular_values,
       rank_convention={"tolerance":1e-4,"scaling":"none; absolute singular values",
                        "coordinates":"Original PEP basis in setup order"},
       rank_credible=all(not any(0.5e-4<v<2e-4 for v in sv) for sv in singular_values),
       certificate_checked=True,grouping_checked=True,certificate_checks=checks,
       coverage_residual=coverage_residual,piece_residual=piece_residual,
       step_residuals=step_residuals,constraint_assignment=term_assignment,S_assignment=S_assignment,
       boundary_constraints=[],boundary_S=[],omitted_constraints=[],coordinates=coords,
       monotonicity="Each increment is a sum of nonnegative multipliers times residuals <=0 minus positive SOS pieces. V_0=0; initial interpolation joins step zero.")
    return ctx,pb,lyap,sample

