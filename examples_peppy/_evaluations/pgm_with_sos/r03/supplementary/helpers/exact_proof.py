"""Exact local scalar identities for proximal gradient."""
from typing import Any
import numpy as np
import sympy as sp
import pepflow as pf

K=pf.Parameter("k")
NN=pf.Parameter("N")
LL=pf.Parameter("L")
RR=pf.Parameter("R")
ks,ns=sp.symbols("k N",integer=True,positive=True)
ls=sp.Symbol("L",positive=True)
rs=sp.Symbol("R",nonnegative=True)
symbolic_values: dict[str,Any]={"k":ks,"N":ns,"L":ls,"R":rs}


def local_context(label,base=False):
    ctx=pf.PEPContext(label).set_as_current()
    ff=pf.SmoothConvexFunction(is_basis=True,tags=[f"f_{{{label}}}"],L=LL)
    gg=pf.ConvexFunction(is_basis=True,tags=[f"g_{{{label}}}"])
    hh=ff+gg
    xs=hh.set_stationary_point("x_{star}")
    x=pf.Vector(is_basis=True,tags=["x_{k}"])
    x0=x if base else pf.Vector(is_basis=True,tags=["x_{0}"])
    ff(x)
    if not base:
        gg(x)
    y=gg.prox(x-ff.grad(x)/LL,1/LL,tag="x_{k+1}")
    ff(y)
    return {"ctx":ctx,"f":ff,"g":gg,"xs":xs,"x":x,"y":y,"x0":x0}


def I_f(e,u,v):
    ff=e["f"]
    return ff(v)-ff(u)+ff.grad(v)*(u-v)+(ff.grad(u)-ff.grad(v))**2/(2*LL)


def I_g(e,u,v):
    gg=e["g"]
    return gg(v)-gg(u)+gg.grad(v)*(u-v)


def Q_step(e,i):
    x,y,xs=e["x"],e["y"],e["xs"]
    ff,gg=e["f"],e["g"]
    ap,a,astar=ff.grad(x),ff.grad(y),ff.grad(xs)
    s=gg.grad(y)
    c1=NN/((2*NN+1-i)*(2*NN-i)*LL)
    u1=i/(2*NN)*a+(2*NN-i)/(2*NN)*ap-astar
    c2=((i-1)/(2*NN-i)*(2*NN+2)/(2*NN+1)
        +2*NN/((2*NN-i)**2*(2*NN+1)))/(2*LL)
    u2=ap+s-LL/(2*NN+1-i)*(x-xs)
    c3=i/(2*NN+1-i)*2*NN/(2*NN+1)/(2*LL)
    u3=(2*NN+1)/(2*NN)*(a+s)-(ap+s)/(2*NN)-LL/(2*NN-i)*(y-xs)
    return c1*u1**2+c2*u2**2+c3*u3**2


def potential(e,x,j):
    ff,gg,xs=e["f"],e["g"],e["xs"]
    d=x-xs
    return (-LL/(4*NN)*(e["x0"]-xs)**2
            +LL*(NN-j)/(2*NN-j)**2*d**2-d*ff.grad(x)/(2*NN-j)
            +(ff.grad(x)-ff.grad(xs))**2/(2*LL*(2*NN-j))
            +(j+1)/(2*NN-j)*(ff(x)-ff(xs))
            +j/(2*NN-j)*(gg(x)-gg(xs)))


def terminal_potential(e):
    ff,gg,xs,y=e["f"],e["g"],e["xs"],e["y"]
    return ff(y)+gg(y)-ff(xs)-gg(xs)-LL/(4*NN)*(e["x0"]-xs)**2


def step_rhs(e,k):
    x,y,xs=e["x"],e["y"],e["xs"]
    denom=(2*NN-k-1)*(2*NN-k)
    return ((2*NN+1)/denom*I_f(e,xs,y)
           +2*NN/denom*I_g(e,xs,y)
           +(k+1)/(2*NN-k)*I_f(e,x,y)
           +k/(2*NN-k)*I_g(e,x,y)-Q_step(e,k+1))


def base_rhs(e):
    x,y,xs=e["x"],e["y"],e["xs"]
    return (1/(2*NN)*I_f(e,xs,x)
           +(2*NN+1)/((2*NN-1)*2*NN)*I_f(e,xs,y)
           +1/(2*NN)*I_f(e,x,y)
           +1/(2*NN-1)*I_g(e,xs,y)-Q_step(e,1))


def terminal_rhs(e):
    x,y,xs=e["x"],e["y"],e["xs"]
    return (1/(NN+1)*I_f(e,xs,y)+2/(NN+1)*I_g(e,xs,y)
           +NN/(NN+1)*I_f(e,x,y)+(NN-1)/(NN+1)*I_g(e,x,y)
           -Q_step(e,NN))


def single_rhs(e):
    x,y,xs=e["x"],e["y"],e["xs"]
    return (sp.Rational(1,2)*I_f(e,xs,x)+sp.Rational(1,2)*I_f(e,xs,y)
           +sp.Rational(1,2)*I_f(e,x,y)+I_g(e,xs,y)-Q_step(e,1))


def components(expression,ctx,values=None):
    vals=symbolic_values if values is None else values
    manager=pf.ExpressionManager(ctx,resolve_parameters=vals)
    evaluated=manager.eval_scalar(expression,sympy_mode=True)
    gram=sp.Matrix(evaluated.inner_prod_coords).applyfunc(sp.factor)
    funcs=sp.Matrix(list(evaluated.func_coords)).applyfunc(sp.factor)
    offset=sp.factor(evaluated.offset)
    return gram,funcs,offset


def check_identity(name,LHS,RHS,e,values=None,display=True):
    diff=LHS-RHS
    gram,funcs,offset=components(diff,e["ctx"],values)
    assert all(v==0 for v in [*gram,*funcs,offset]),(name,gram,funcs,offset)
    if display:
        labels=[str(v) for v in e["ctx"].basis_vectors()]
        print(name,"Gram residual:")
        pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(gram,dtype=object),labels,labels))
        print(name,"function residual:",funcs.T,"offset:",offset)
    return {"name":name,"gram_zero":True,"function_zero":True,"offset_zero":True,
            "shape":list(gram.shape)}

