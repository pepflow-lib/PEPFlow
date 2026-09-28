from typing import Any
import sympy as sp
import numpy as np
import pepflow as pf

b4=json.loads((notebook_dir/'state/dual_feg_b4.json').read_text())
assert b4['numerical_reconstruction']['certificate_id']==b4['certificate_id']
assert b4['numerical_reconstruction']['passed']
# The preceding notebook cells freshly reconstruct the unchanged B4 sample.
assert certificate_checked and grouping_checked


def symbolic_components(expression,manager):
    evaluated=manager.eval_scalar(pf.Scalar.zero()+expression,sympy_mode=True)
    gram=sp.Matrix(evaluated.inner_prod_coords).applyfunc(sp.simplify)
    functions=sp.Matrix(list(evaluated.func_coords)).applyfunc(sp.simplify)
    offset=sp.simplify(sp.sympify(evaluated.offset))
    return gram,functions,offset


def verify_exact(name,LHS,RHS,manager):
    gram,functions,offset=symbolic_components(LHS-RHS,manager)
    names=[str(v) for v in manager.context.basis_vectors()]
    pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(gram,dtype=object),names,names))
    print(name,'function residual:',functions,'constant residual:',offset)
    good=all(v==0 for v in [*gram,*functions,offset])
    assert good,name
    print(name,'exact all-component identity:',good)
    return good

Ts,Ns=sp.symbols('t N',integer=True,positive=True)
Ls=sp.Symbol('L',positive=True)
aa,bb,cc,dd,ee,nu_s,mu_s=sp.symbols('a b c d e nu mu',real=True)
Tp=pf.Parameter('t_exact')
Np=pf.Parameter('N_exact')
Lp=pf.Parameter('L_exact')
Ap,Bp,Cp,Dp,Ep=map(pf.Parameter,['a_exact','b_exact','c_exact','d_exact','e_exact'])
nup,mup=pf.Parameter('nu_exact'),pf.Parameter('mu_exact')
ctx_der=pf.PEPContext('dual_feg_coefficient_derivation').set_as_current()
x=pf.Vector(is_basis=True,tags=['x_{k}'])
z=pf.Vector(is_basis=True,tags=['z_{k}'])
xN=pf.Vector(is_basis=True,tags=['x_{N}'])
x0=pf.Vector(is_basis=True,tags=['x_{0}'])
A_der=pf.LipschitzMonotoneOperator(is_basis=True,tags=['A_{derive}'],L=Lp)
u=A_der(x)
G=A_der(xN)
y=(x-(z+u)/Lp).add_tag('y_{k}')
h=A_der(y)
xp=(y-(Tp-1)/Tp/Lp*(h-u)).add_tag('x_{k+1}')
zp=((Tp-1)/Tp*z-h/Tp).add_tag('z_{k+1}')


def ansatz(t,zz,xx):
    return Ep/Np*(x0-xN)*G+Ap*zz**2+Bp/t*zz*(xx-xN)+Cp*zz*G+Dp/t*(xx-xN)*G

lip=(u-h)**2-Lp**2*(x-y)**2
mon=-(G-h)*(xN-y)
LHS=ansatz(Tp-1,zp,xp)-ansatz(Tp,z,x)
RHS=nup*lip+mup*mon
mapping: dict[str, Any]={'t_exact':Ts,'N_exact':Ns,'L_exact':Ls,'a_exact':aa,'b_exact':bb,'c_exact':cc,'d_exact':dd,'e_exact':ee,'nu_exact':nu_s,'mu_exact':mu_s}
pm_der=pf.ExpressionManager(ctx_der,resolve_parameters=mapping)
gram_eq,func_eq,offset_eq=symbolic_components(LHS-RHS,pm_der)
equations=[v for v in [*gram_eq,*func_eq,offset_eq] if v!=0]
solutions=sp.solve(equations,[aa,bb,cc,nu_s,mu_s],dict=True)
print('Coefficient solution family:',solutions)
assert len(solutions)==1
solution=solutions[0]
expected={aa:-dd/(2*Ls),bb:dd,cc:-dd/Ls,nu_s:dd/(2*Ls*Ts**2),mu_s:dd/(Ts*(Ts-1))}
assert all(sp.simplify(solution[key]-value)==0 for key,value in expected.items())
print('The anchor coefficient e does not enter the step; the base condition will set e=-d.')
print('Choose d=4L to normalize the terminal squared-residual coefficient to 2.')

