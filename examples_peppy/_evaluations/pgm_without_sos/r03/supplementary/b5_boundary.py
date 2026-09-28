f_boundary=pf.SmoothConvexFunction(is_basis=True,tags=['f_{boundary}'],L=Lpar)
g_boundary=pf.ConvexFunction(is_basis=True,tags=['g_{boundary}'])
ctx_boundary=pf.PEPContext('symbolic_boundary').set_as_current()
star=(f_boundary+g_boundary).set_stationary_point('x_{star}')
x=pf.Vector(is_basis=True,tags=['x_{N-1}'])
y=g_boundary.prox(x-f_boundary.grad(x)/Lpar,1/Lpar,tag='x_{N}')
g_boundary(x)
f_boundary(y)
d=x-star
p=(f_boundary.grad(x)-f_boundary.grad(star))/Lpar
z=(f_boundary.grad(y)-f_boundary.grad(star))/Lpar
q=(g_boundary.grad(y)+f_boundary.grad(star))/Lpar
Vprevious=P('alpha_terminal')*d**2-P('inv_terminal')*d*f_boundary.grad(x)-P('t_terminal')*(f_boundary.grad(x)-f_boundary.grad(star))**2+P('af_terminal')*(f_boundary(x)-f_boundary(star))+P('bg_terminal')*(g_boundary(x)-g_boundary(star))
Vfinal=f_boundary(y)-f_boundary(star)+g_boundary(y)-g_boundary(star)
Ifstar=f_boundary(y)-f_boundary(star)-f_boundary.grad(y)*(y-star)+(f_boundary.grad(y)-f_boundary.grad(star))**2/(2*Lpar)
Ifpair=f_boundary(y)-f_boundary(x)+f_boundary.grad(y)*(x-y)+(f_boundary.grad(x)-f_boundary.grad(y))**2/(2*Lpar)
Igstar=g_boundary(y)-g_boundary(star)-g_boundary.grad(y)*(y-star)
Igpair=g_boundary(y)-g_boundary(x)+g_boundary.grad(y)*(x-y)
Qterminal=Lpar/2*((z+q-P('inv_terminal')*(d-p))**2+(q+P('af_terminal')*p-P('inv_terminal')*d)**2)
LHS=Vfinal-Vprevious
RHS=(1-P('af_terminal'))*Ifstar+P('af_terminal')*Ifpair+(1-P('bg_terminal'))*Igstar+P('bg_terminal')*Igpair-Qterminal
params_boundary: dict[str,Any]={'L_symbolic':L_symbol,'alpha_terminal':L_symbol/(N_symbol+1)**2,'inv_terminal':1/(N_symbol+1),'t_terminal':(N_symbol-1)/(2*L_symbol*(N_symbol+1)**2),'af_terminal':N_symbol/(N_symbol+1),'bg_terminal':(N_symbol-1)/(N_symbol+1)}
pm_boundary=pf.ExpressionManager(ctx_boundary,resolve_parameters=params_boundary)
diff=LHS-RHS
boundary_verified=exact_check('Terminal increment, N>=2',diff,pm_boundary,ctx_boundary)
