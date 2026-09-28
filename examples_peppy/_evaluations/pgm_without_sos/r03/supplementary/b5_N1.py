# The one-step horizon is checked independently, without evaluating g(x_0).
f_one=pf.SmoothConvexFunction(is_basis=True,tags=['f_{one}'],L=Lpar)
g_one=pf.ConvexFunction(is_basis=True,tags=['g_{one}'])
ctx_one=pf.PEPContext('symbolic_N1').set_as_current()
star=(f_one+g_one).set_stationary_point('x_{star}')
x=pf.Vector(is_basis=True,tags=['x_{0}'])
y=g_one.prox(x-f_one.grad(x)/Lpar,1/Lpar,tag='x_{1}')
f_one(y)
d=x-star
p=(f_one.grad(x)-f_one.grad(star))/Lpar
z=(f_one.grad(y)-f_one.grad(star))/Lpar
q=(g_one.grad(y)+f_one.grad(star))/Lpar
If0=f_one(x)-f_one(star)-f_one.grad(x)*d+(f_one.grad(x)-f_one.grad(star))**2/(2*Lpar)
If1=f_one(y)-f_one(star)-f_one.grad(y)*(y-star)+(f_one.grad(y)-f_one.grad(star))**2/(2*Lpar)
If01=f_one(y)-f_one(x)+f_one.grad(y)*(x-y)+(f_one.grad(x)-f_one.grad(y))**2/(2*Lpar)
Ig1=g_one(y)-g_one(star)-g_one.grad(y)*(y-star)
Qone=Lpar/2*((z+q-(d-p)/2)**2+(q+p/2-d/2)**2)
LHS=f_one(y)-f_one(star)+g_one(y)-g_one(star)-Lpar*d**2/4
RHS=sp.Rational(1,2)*If0-Lpar*p**2/4+sp.Rational(1,2)*If1+sp.Rational(1,2)*If01+Ig1-Qone
pm_one=pf.ExpressionManager(ctx_one,resolve_parameters={'L_symbolic':L_symbol})
diff=LHS-RHS
small_horizon_verified=exact_check('N=1 direct base-terminal identity',diff,pm_one,ctx_one)
