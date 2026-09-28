"""Derive coefficient relations from all local scalar coordinates."""
from typing import cast
import sympy as sp
import pepflow as pf

from exact_proof import K,symbolic_values,components,step_rhs,local_context,ks,ns,ls


def coefficient_ansatz(e,x,prefix,values,unknowns):
    ff,gg,xs=e["f"],e["g"],e["xs"]
    vectors=[e["x0"]-xs,x-xs,ff.grad(x),ff.grad(xs)-ff.grad(x)]
    expression=pf.Scalar.zero()
    for i in range(4):
        for j in range(i,4):
            name=f"{prefix}_c{i}{j}"
            symbol=sp.Symbol(name)
            values[name]=symbol
            unknowns.append(symbol)
            expression+=(1 if i==j else 2)*pf.Parameter(name)*vectors[i]*vectors[j]
    for tag,term in [("p",ff(x)-ff(xs)),("q",gg(x)-gg(xs))]:
        name=f"{prefix}_{tag}"
        symbol=sp.Symbol(name)
        values[name]=symbol
        unknowns.append(symbol)
        expression+=pf.Parameter(name)*term
    return expression


def closed_coefficients(j,n,ell):
    j,n,ell=(cast(sp.Expr,sp.sympify(v)) for v in (j,n,ell))
    C=sp.zeros(4)
    C[0,0]=-ell/(4*n)
    C[1,1]=ell*(n-j)/(2*n-j)**2
    C[1,2]=C[2,1]=-1/(2*(2*n-j))
    C[3,3]=1/(2*ell*(2*n-j))
    return C,(j+1)/(2*n-j),j/(2*n-j)


def derive():
    e=local_context("derive")
    values=dict(symbolic_values)
    unknowns=[]
    old=coefficient_ansatz(e,e["x"],"old",values,unknowns)
    new=coefficient_ansatz(e,e["y"],"new",values,unknowns)
    gram,funcs,offset=components(new-old-step_rhs(e,K),e["ctx"],values)
    equations=[v for v in [*gram,*funcs,offset] if v!=0]
    solution=sp.linsolve(equations,unknowns)
    solved=next(iter(solution))
    free=set().union(*(v.free_symbols for v in solved))-set((ks,ns,ls))
    substitution={}
    for prefix,j in [("old",ks),("new",ks+1)]:
        C,p,q=closed_coefficients(j,ns,ls)
        for i in range(4):
            for m in range(i,4):
                substitution[sp.Symbol(f"{prefix}_c{i}{m}")]=C[i,m]
        substitution[sp.Symbol(f"{prefix}_p")]=p
        substitution[sp.Symbol(f"{prefix}_q")]=q
    assert all(sp.factor(v.subs(substitution)-substitution[u])==0 for u,v in zip(unknowns,solved))
    assert all(sp.factor(v.subs(substitution))==0 for v in equations)
    return e,unknowns,equations,solved,free,substitution

