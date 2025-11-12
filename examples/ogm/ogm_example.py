"""
This code tests Optimized Gradient Method (OGM) which is the exact optimal method
that reduces function value respect to initial distance to solution for L-smooth
convex functions. Introduced in "Optimized first-order methods for smooth convex
minimization" by Donghwan Kim, Jeffrey A Fessler (2016).
"""

import functools

import numpy as np

import pepflow as pf

eta = 1
L = 1
N = 3


@functools.cache
def theta(i, N):
    if i == -1:
        return 0
    if i == N:
        return 1 / 2 * (1 + np.sqrt(8 * theta(N - 1, N) ** 2 + 1))
    return 1 / 2 * (1 + np.sqrt(4 * theta(i - 1, N) ** 2 + 1))


ogm = pf.PEPContext("ogm").set_as_current()
pep_builder = pf.PEPBuilder(ogm)

f = pf.declare_func(pf.SmoothConvexFunction, "f", L=1)
x_0 = pep_builder.add_init_point("x_0")
x = x_0
z = x_0

eta = 1 / L
for i in range(N):
    y = x - eta * f.grad(x)
    z = z - 2 * eta * theta(i, N) * f.grad(x)
    x = (1 - 1 / theta(i + 1, N)) * y + 1 / theta(i + 1, N) * z

    z.add_tag(f"z_{i + 1}")
    x.add_tag(f"x_{i + 1}")

x_star = f.set_stationary_point("x_star")
pep_builder.add_initial_constraint(
    ((x_0 - x_star) ** 2).le(1, name="initial_condition")
)

x_N = ogm.get_by_tag(f"x_{N}")
pep_builder.set_performance_metric(f(x_N) - f(x_star))

result = pep_builder.solve_primal()
print(result.opt_value)

result = pep_builder.solve_dual()
print(result.opt_value)
