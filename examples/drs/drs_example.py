"""
This code tests Douglas--Rachford splitting methods, with performance metric considered in
"Exact worst-case convergence rates for Douglas--Rachford and Davis--Yin splitting methods"
by Edward Duc Hien Nguyen, Jaewook J. Suh, Xin Jiang, Shiqian Ma (2025).
"""

import pepflow as pf

drs = pf.PEPContext("drs").set_as_current()
pep_builder = pf.PEPBuilder(drs)
alpha = 1.0
N = 2

# Declare two convex functions.
f = pf.declare_func(pf.ConvexFunction, "f")
g = pf.declare_func(pf.ConvexFunction, "g")

# Declare the initial points.
x = pep_builder.add_init_point("x_{{0}}")
u = pep_builder.add_init_point("u_{{0}}")

# Declare the points used in the primal-dual gap function.
x_tilde = pf.Vector(is_basis=True)
x_tilde.add_tag("x_{{tilde}}")
u_tilde = pf.Vector(is_basis=True)
u_tilde.add_tag("u_{{tilde}}")

pep_builder.add_initial_constraint(
    ((1.0 / alpha) * (x - x_tilde) ** 2 + alpha * (u - u_tilde) ** 2).le(
        1, name="initial_condition"
    )
)

x_sum = pf.Vector.zero()
u_sum = pf.Vector.zero()

for i in range(N):
    x_old = x

    x = f.proximal_step(x - alpha * u, alpha).add_tag(f"x_{i + 1}")

    t = u + 1 / alpha * (2 * x - x_old)
    p = g.proximal_step(alpha * t, alpha)
    u = t - 1 / alpha * p
    u.add_tag(f"u_{i + 1}")

    x_sum = x_sum + x
    u_sum = u_sum + u

x_avg = x_sum / float(N)
u_avg = u_sum / float(N)
x_avg.add_tag("x_{{avg}}")
u_avg.add_tag("u_{{avg}}")

# Define p_tilde and p_avg such that u_tilde \in \partial g(p_tilde) and u_avg \in \partial g(u_avg)
p_tilde = pf.Vector(is_basis=True)
p_tilde.add_tag("p_{{tilde}}")
p_avg = pf.Vector(is_basis=True)
p_avg.add_tag("p_{{avg}}")
g.add_point_with_grad_restriction(p_tilde, u_tilde)
g.add_point_with_grad_restriction(p_avg, u_avg)

pep_builder.set_performance_metric(
    f(x_avg)
    - f(x_tilde)
    + g(p_tilde)
    - g(p_avg)
    + u_tilde * x_avg
    - u_tilde * p_tilde
    - u_avg * x_tilde
    + u_avg * p_avg
)

result = pep_builder.solve_primal()
print(result.opt_value)

result = pep_builder.solve_dual()
print(result.opt_value)
