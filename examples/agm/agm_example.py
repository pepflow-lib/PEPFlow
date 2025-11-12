"""
This code tests Nesterov's accelerated gradient method (AGM), which is arguably the first accelerated method,
introduced in "A Method of Solving a Convex Programming Problem with Convergence Rate O(1/k^2)" by Yurii Nesterov (1983).
AGM reduces the function value with respect to the initial distance to the solution for L-smooth convex functions and achieves an O(1/k²) rate.
This code recovers the rate for the secondary sequence, based on the values introduced in
"Optimized First-Order Methods for Smooth Convex Minimization" by Donghwan Kim and Jeffrey A. Fessler (2016).
"""

import functools
import itertools

import numpy as np

import pepflow as pf

agm = pf.PEPContext("agm").set_as_current()
pep_builder = pf.PEPBuilder(agm)
eta = 1
L = 1
N = 3


@functools.cache
def theta(i):
    if i == -1:
        return 0
    return 1 / 2 * (1 + np.sqrt(4 * theta(i - 1) ** 2 + 1))


f = pf.declare_func(pf.SmoothConvexFunction, "f", L=1)
x_0 = pep_builder.add_init_point("x_0")
x = x_0
z = x_0

eta = 1 / L
for i in range(N):
    y = x - eta * f.grad(x)
    z = z - eta * theta(i) * f.grad(x)
    x = (1 - 1 / theta(i + 1)) * y + 1 / theta(i + 1) * z

    z.add_tag(f"z_{i + 1}")
    x.add_tag(f"x_{i + 1}")

x_star = f.set_stationary_point("x_star")
pep_builder.add_initial_constraint(
    ((x_0 - x_star) ** 2).le(1, name="initial_condition")
)

x_N = agm.get_by_tag(f"x_{N}")
pep_builder.set_performance_metric(f(x_N) - f(x_star))

result = pep_builder.solve_primal()
print(f"Optimal value: {result.opt_value}")

desired_upper_bound = L / (2 * theta(N) ** 2)
print(
    "Is the optimal value less than or equal to our desired upper bound?",
    result.opt_value <= desired_upper_bound,
)
print(f"Desired upper bound is: {desired_upper_bound}")

# Additional dual constraints
relaxed_constraints = []
index_set = list(range(N + 1)) + ["star"]
for i, j in itertools.product(index_set, index_set):
    if i != j and i != "star" and j != i + 1:
        relaxed_constraints.append(f"f:x_{i},x_{j}")
pep_builder.set_relaxed_constraints(relaxed_constraints)

for i in range(N + 1):
    pep_builder.add_dual_val_constraint(
        f"f:x_{i},x_{i + 1}", "==", theta(i) ** 2 / theta(N) ** 2
    )

# Solve the dual problem with the additional constraint and compare it with the desired convergence rate
result = pep_builder.solve_dual()
print(f"Optimal value with the additional constraints: {result.opt_value}")
