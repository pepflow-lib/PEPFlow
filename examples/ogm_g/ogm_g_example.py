"""
This code tests OGM-G which is the state-of-the-art method
that reduces gradient norm square respect to initial function value gap for L-smooth
convex functions. Introduced in "Optimizing the Efficiency of First-Order Methods for
Decreasing the Gradient of Smooth Convex Functions" by Donghwan Kim, Jeffrey A Fessler (2021).
"""

import functools

import numpy as np

import pepflow as pf

ogm_g = pf.PEPContext("ogm_g").set_as_current()
pep_builder = pf.PEPBuilder(ogm_g)
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


def reverse_theta(i, N):
    return theta(N - i, N)


f = pf.declare_func(pf.SmoothConvexFunction, "f", L=1)
x_0 = pep_builder.add_init_point("x_0")
x = x_0
z = x_0

eta = 1 / L
z = z - eta * (reverse_theta(0, N) + 1) / 2 * f.grad(x)
z.add_tag(f"z_{1}")

for i in range(1, N + 1):
    y = x - eta * f.grad(x)
    x = (reverse_theta(i + 1, N) / reverse_theta(i, N)) ** 4 * y + (
        1 - (reverse_theta(i + 1, N) / reverse_theta(i, N)) ** 4
    ) * z
    z = z - eta * reverse_theta(i, N) * f.grad(x)

    x.add_tag(f"x_{i}")
    z.add_tag(f"z_{i + 1}")

x_star = f.set_stationary_point("x_star")

pep_builder.add_initial_constraint((f(x_0) - f(x_star)).le(1, name="initial_condition"))

x_N = ogm_g.get_by_tag(f"x_{N}")

pep_builder.set_performance_metric((f.grad(x_N)) ** 2)

result = pep_builder.solve_primal()
print(result.opt_value)

result = pep_builder.solve_dual()
print(result.opt_value)
