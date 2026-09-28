"""Basis search and every-index reconstruction for the selected partial sums."""
import itertools
import numpy as np
import pepflow as pf
import sympy as sp
from pepflow.utils import NUMERICAL_TYPE
from pepflow.lyapunov_utils import (
    vectors_in_column_space,find_basis_with_sparsest_coefficients,
    find_symmetric_coefficient_matrix)
from pgm_setup import f,g
from transport_grouping import construct
from certificates import maxabs


def V_k_basis(ctx,k,n):
    if k==0:
        return []
    d0=ctx["x_0"]-ctx["x_star"]
    if k==n:
        return [d0]
    return [d0,ctx[f"x_{k}"]-ctx["x_star"],f.grad(ctx[f"x_{k}"]),
            f.grad(ctx["x_star"])-f.grad(ctx[f"x_{k}"])]


def V_k_basis_labels(k,n):
    if k==0:
        return []
    if k==n:
        return ["d_0"]
    return ["d_0","d_k","a_k","a_star-a_k"]


def sample_structure(ctx,k,n,C,fg,gg,offset):
    vectors=V_k_basis(ctx,k,n)
    quadratic=sum((float(C[i,j])*vectors[i]*vectors[j]
                    for i,j in np.ndindex(C.shape)),pf.Scalar.zero())
    if k==0:
        return quadratic+offset
    x=ctx[f"x_{k}"]
    return quadratic+fg*(f(x)-f(ctx["x_star"]))+gg*(g(x)-g(ctx["x_star"]))+offset


def discover(certificate,verbose=True):
    ctx,pb,lyap,observation=construct(certificate,False)
    n=certificate["N_verify"]
    pm=pf.ExpressionManager(ctx,resolve_parameters={"L":sp.S.One,"R":sp.S.One})
    params: dict[str, NUMERICAL_TYPE] = {"L":sp.S.One,"R":sp.S.One}
    assert observation["rank_profile"]==certificate["rank_profile"]
    for k,V in enumerate(lyap):
        q=pm.eval_scalar(V)
        for actual,saved in ((q.inner_prod_coords,certificate["lyap_inner_prod_coords"][k]),
                             (q.func_coords,certificate["lyap_func_coords"][k]),
                             (q.offset,certificate["lyap_offsets"][k])):
            assert np.allclose(np.asarray(actual,dtype=float),saved,atol=1e-4,rtol=1e-5)
    base=[(str(v),v) for v in ctx.basis_vectors()]
    base += [(f"d_{k}",ctx[f"x_{k}"]-ctx["x_star"]) for k in range(n+1)]
    base += [(f"a_star-a_{k}",f.grad(ctx["x_star"])-f.grad(ctx[f"x_{k}"])) for k in range(n+1)]
    pairs=base+[(a+"-"+b,u-v) for (a,u),(b,v) in itertools.combinations(base,2)]
    candidates=[]
    seen=[]
    for label,v in pairs:
        coords=np.asarray(pm.eval_vector(v).coords,dtype=float)
        if np.linalg.norm(coords)<1e-7 or any(np.allclose(coords,c,atol=1e-10,rtol=0) for c in seen):
            continue
        seen.append(coords)
        candidates.append((label,v))
    outputs=[]
    coeffs={}
    for k,V in enumerate(lyap):
        q=pm.eval_scalar(V)
        target=np.asarray(q.inner_prod_coords,dtype=float)
        rank=observation["rank_profile"][k]
        basis=V_k_basis(ctx,k,n)
        search_labels=[]
        zeros=0
        if rank:
            in_col=vectors_in_column_space(V,[v for _,v in candidates],pep_context=ctx,
                                          resolve_parameters=params,rtol=1e-4,atol=1e-4)
            if verbose:
                print(f"V_{k} column-space candidates:")
                for label,v in candidates:
                    if any(v is u for u in in_col):
                        print("  ",label)
            searched,Csearch=find_basis_with_sparsest_coefficients(
                V,in_col,pep_context=ctx,resolve_parameters=params,
                zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
            assert len(searched)==rank
            search_labels=[label for v in searched for label,u in candidates if u is v]
            zeros=int(np.sum(abs(Csearch)<1e-6))
            if verbose:
                print(f"k={k}: rank {rank}; sparse basis: {search_labels}; zero coefficients: {zeros}/{Csearch.size}")
            B=np.column_stack([pm.eval_vector(v).coords for v in basis]).astype(float)
            assert np.linalg.matrix_rank(B,tol=1e-7)==len(basis)==rank
            C=find_symmetric_coefficient_matrix(V,basis,pep_context=ctx,
                resolve_parameters=params,indep_tol=1e-7,span_tol=1e-5)
            err=float(np.linalg.norm(B@C@B.T-target))
            assert err<=1e-5*max(1.,float(np.linalg.norm(target)))
        else:
            C=np.zeros((0,0))
            err=float(np.linalg.norm(target))
            assert err<=1e-5
        coeffs[str(k)]=C.tolist()
        if k:
            ff=pm.eval_scalar(f(ctx[f"x_{k}"])-f(ctx["x_star"])).func_coords
            gf=pm.eval_scalar(g(ctx[f"x_{k}"])-g(ctx["x_star"])).func_coords
            FG=np.column_stack([ff,gf]).astype(float)
            fg,gg=np.linalg.lstsq(FG,np.asarray(q.func_coords,dtype=float),rcond=None)[0]
        else:
            fg=gg=0.
        expr=sample_structure(ctx,k,n,C,float(fg),float(gg),float(q.offset))
        difference=pm.eval_scalar(expr-V)
        residuals={"gram":maxabs(difference.inner_prod_coords),
                   "function":maxabs(difference.func_coords),"offset":maxabs(difference.offset)}
        assert max(residuals.values())<=1e-4
        row={"k":k,"rank":rank,"search_basis":search_labels,"zero_coefficients":zeros,
             "basis_labels":V_k_basis_labels(k,n),"quadratic_error":err,
             "C":C.tolist(),"f_gap_coefficient":float(fg),"g_gap_coefficient":float(gg),
             "offset":float(q.offset),"component_residuals":residuals}
        outputs.append(row)
        if verbose:
            print(f"k={k}: rank {rank} basis {V_k_basis_labels(k,n)}; reconstruction {err}")
            print("Function gaps and offset:",fg,gg,q.offset)
    return ctx,pb,lyap,coeffs,outputs

