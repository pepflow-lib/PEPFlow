import sympy as sp
import numpy as np
import pepflow as pf

n_symbol, i_symbol = sp.symbols('N i', integer=True, positive=True)
ell_symbol = sp.symbols('L', positive=True)


def analytic_potential(point, fs, gs, xs, x0, index, horizon, ell):
    k,n = index,horizon
    d = 2*n-k
    gap_f=fs(point)-fs(xs)
    gap_g=gs(point)-gs(xs)
    a,astar=fs.grad(point),fs.grad(xs)
    dx=point-xs
    return ((k+1)/d*gap_f+k/d*gap_g-a*dx/d+(a-astar)**2/(2*d*ell)
            +ell*(n-k)/d**2*dx**2-ell/(4*n)*(x0-xs)**2)


def smooth_residual(fs, first, second, ell):
    return fs(second)-fs(first)+fs.grad(second)*(first-second)+(fs.grad(first)-fs.grad(second))**2/(2*ell)


def convex_residual(gs, first, second):
    return gs(second)-gs(first)+gs.grad(second)*(first-second)


def local_squares(fs, gs, xp, xn, xs, index, horizon, ell):
    i,n=index,horizon
    ap,a,astar,s=fs.grad(xp),fs.grad(xn),fs.grad(xs),gs.grad(xn)
    c1=n/((2*n+1-i)*(2*n-i))/ell
    u1=i/(2*n)*a+(2*n-i)/(2*n)*ap-astar
    c2=((i-1)/(2*n-i)*(2*n+2)/(2*n+1)+2*n/((2*n-i)**2*(2*n+1)))/(2*ell)
    u2=ap+s-ell/(2*n+1-i)*(xp-xs)
    c3=i/(2*n+1-i)*(2*n)/(2*n+1)/(2*ell)
    u3=(2*n+1)/(2*n)*(a+s)-(ap+s)/(2*n)-ell/(2*n-i)*(xn-xs)
    return c1*u1**2+c2*u2**2+c3*u3**2


def local_contribution(fs,gs,xp,xn,xs,index,horizon,ell,terminal=False,include_previous_g=True):
    i,n=index,horizon
    wf=(1/(n+1) if terminal else (2*n+1)/((2*n-i)*(2*n+1-i)))
    wg=(2/(n+1) if terminal else 2*n/((2*n-i)*(2*n+1-i)))
    total=wf*smooth_residual(fs,xs,xn,ell)+i/(2*n+1-i)*smooth_residual(fs,xp,xn,ell)
    total+=wg*convex_residual(gs,xs,xn)
    if include_previous_g:
        total+=(i-1)/(2*n+1-i)*convex_residual(gs,xp,xn)
    return total-local_squares(fs,gs,xp,xn,xs,i,n,ell)


def symbolic_components(expression,manager):
    ev=manager.eval_scalar(expression,sympy_mode=True)
    gram=sp.Matrix(ev.inner_prod_coords).applyfunc(sp.factor)
    funcs=sp.Matrix(list(ev.func_coords)).applyfunc(sp.factor)
    offset=sp.factor(ev.offset)
    return gram,funcs,offset


def verify_identity(label,expression,manager):
    gram,funcs,offset=symbolic_components(expression,manager)
    assert all(v==0 for v in [*gram,*funcs,offset]),(label,gram,funcs,offset)
    labels=[str(v) for v in manager.context.basis_vectors()]
    pf.pprint_labeled_matrix(np.array(gram,dtype=object),labels,labels)
    print(label,'Gram residual zero; function residual:',funcs.T,'offset:',offset)
    return True
