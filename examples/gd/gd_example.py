import pepflow as pf

gd = pf.PEPContext("gd").set_as_current()
pep_builder = pf.PEPBuilder(gd)
eta = 1
L = 1

f = pf.declare_func(pf.SmoothConvexFunction, "f", L=1)
x = pep_builder.add_init_point("x_0")
x_star = f.set_stationary_point("x_star")
pep_builder.add_initial_constraint(((x - x_star) ** 2).le(1, name="initial_condition"))

for i in range(1):
    x = x - eta * f.grad(x)
    x.add_tag(f"x_{i + 1}")

pep_builder.set_performance_metric(f(x) - f(x_star))

result = pep_builder.solve_primal()
print(result.opt_value)

result = pep_builder.solve_dual()
print(result.opt_value)
