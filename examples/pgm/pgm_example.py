import pepflow as pf

pgm = pf.PEPContext("pgm").set_as_current()
pep_builder = pf.PEPBuilder(pgm)
eta = 1
N = 2

f = pf.declare_func(pf.SmoothConvexFunction, "f", L=1)
g = pf.declare_func(pf.ConvexFunction, "g")

h = f + g
h.add_tag("h")

x = pep_builder.add_init_point("x_0")
x_star = h.set_stationary_point("x_star")
pep_builder.add_initial_constraint(((x - x_star) ** 2).le(1, name="initial_condition"))

for i in range(N):
    # Gradient step
    y = x - eta * f.grad(x)
    y.add_tag(f"y_{i + 1}")
    # Apply proximal operator with respect to g onto y and return the output as x.
    x = g.proximal_step(y, eta)
    x.add_tag(f"x_{i + 1}")
pep_builder.set_performance_metric(h(x) - h(x_star))

result = pep_builder.solve_primal()
print(result.opt_value)

result = pep_builder.solve_dual()
print(result.opt_value)
