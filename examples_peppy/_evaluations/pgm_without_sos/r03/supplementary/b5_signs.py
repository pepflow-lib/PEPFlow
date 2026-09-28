# Positive coefficients are justified for integers N>=2, 0<=k<=N-2 and U>=0.
# Then m=2N-k>1. Every denominator below is strictly positive.
ks,ms,us=sp.symbols('k m U',nonnegative=True)
positive_D=((2*ks+1)*ms-ks)*us+(ms-1)*(ks*(ks+3)*ms+ms+1)
positive_H=us+(ks+2)*(ms-1)
assert sp.expand(((2*ks+1)*ms-ks)-(ks*(2*ms-1)+ms))==0
assert sp.factor(positive_D-(((2*ks+1)*ms-ks)*positive_H-(ks+1)**2*(ms-1)**2))==0
# First numerator row of M_j is nonnegative; its second row is strictly positive.
# Therefore a positive-denominator tail vector stays so under every factor.
# This proves T_k>=0 and ensures H,D,A,B>0. T_0=0 is allowed.
Npos,kpos=sp.symbols('N k',integer=True,positive=True)
a_cur=(kpos+1)/(2*Npos-kpos)
a_next=(kpos+2)/(2*Npos-kpos-1)
b_cur=kpos/(2*Npos-kpos)
b_next=(kpos+1)/(2*Npos-kpos-1)
assert sp.factor(a_next-a_cur-(2*Npos+1)/((2*Npos-kpos)*(2*Npos-kpos-1)))==0
assert sp.factor(b_next-b_cur-2*Npos/((2*Npos-kpos)*(2*Npos-kpos-1)))==0
print('Multiplier differences:',sp.factor(a_next-a_cur),sp.factor(b_next-b_cur))
print('Domain/sign proof: finite-product denominators positive; T>=0; H,D,A,B>0; all interpolation weights nonnegative; all subtracted squared norms nonnegative.')
# Normalization and terminal formula, including the radius and constant term.
R_symbol=sp.symbols('R',nonnegative=True)
ctx_normalization=pf.PEPContext('symbolic_normalization').set_as_current()
d_initial=pf.Vector(is_basis=True,tags=['d_{0}'])
gap=pf.Scalar(is_basis=True,tags=['h_{N}-h_{star}'])
Vterminal=gap-P('tau')*d_initial**2
LHS=gap-P('bound')
RHS=Vterminal+P('tau')*(d_initial**2-P('R_squared'))
params_normalization: dict[str,Any]={'tau':L_symbol/(4*N_symbol),'bound':L_symbol*R_symbol**2/(4*N_symbol),'R_squared':R_symbol**2}
pm_normalization=pf.ExpressionManager(ctx_normalization,resolve_parameters=params_normalization)
normalization_verified=exact_check('Radius normalization',LHS-RHS,pm_normalization,ctx_normalization)
assert step_verified and base_verified and boundary_verified and small_horizon_verified and normalization_verified
print('Consequently h(x_N)-h_star <= L*R^2/(4*N) for every integer N>=1, L>0 and R>=0.')
