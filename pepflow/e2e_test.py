# Copyright: 2025 The PEPFlow Developers
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import functools
import itertools
import math

import numpy as np

from pepflow import function, operator
from pepflow import parameter as pm
from pepflow import pep
from pepflow import pep_context as pc
from pepflow import vector
from pepflow.constraint import ScalarConstraint


def test_gd_e2e():
    ctx = pc.PEPContext("gd").set_as_current()
    pep_builder = pep.PEPBuilder(ctx)
    eta = 1
    N = 9

    f = function.SmoothConvexFunction(is_basis=True, tags=["f"], L=1)
    x = pep_builder.add_init_point("x_0")
    x_star = f.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        ((x - x_star) ** 2).le(1, name="initial_condition")
    )

    # We first build the algorithm with the largest number of iterations.
    for i in range(N):
        x = x - eta * f.grad(x)
        x.add_tag(f"x_{i + 1}")

    # To achieve the sweep, we can just update the performance_metric.
    for i in range(1, N + 1):
        p = ctx.get_by_tag(f"x_{i}")
        pep_builder.set_performance_metric(f.func_val(p) - f.func_val(x_star))
        result = pep_builder.solve_primal()
        expected_opt_value = 1 / (4 * i + 2)
        assert math.isclose(result.opt_value, expected_opt_value, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual()
        assert math.isclose(dual_result.opt_value, expected_opt_value, rel_tol=1e-3)


def test_gd_strongly_convex_e2e():
    ctx = pc.PEPContext("gd").set_as_current()
    pep_builder = pep.PEPBuilder(ctx)
    eta = 1
    N = 9

    f = function.SmoothStronglyConvexFunction(is_basis=True, tags=["f"], L=1, mu=0.1)
    x = pep_builder.add_init_point("x_0")
    x_star = f.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        ((x - x_star) ** 2).le(1, name="initial_condition")
    )

    # We first build the algorithm with the largest number of iterations.
    for i in range(N):
        x = x - eta * f.grad(x)
        x.add_tag(f"x_{i + 1}")

    # To achieve the sweep, we can just update the performance_metric.
    kappa = 0.1
    for i in range(1, N + 1):
        p = ctx.get_by_tag(f"x_{i}")
        pep_builder.set_performance_metric(f.func_val(p) - f.func_val(x_star))
        result = pep_builder.solve_primal()
        expected_opt_value = (
            1 / 2 * (kappa / ((kappa - 1) + 1 / (1 - kappa) ** (2 * i)))
        )
        assert math.isclose(result.opt_value, expected_opt_value, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual()
        assert math.isclose(dual_result.opt_value, expected_opt_value, rel_tol=1e-3)


def test_gd_diff_stepsize_e2e():
    ctx = pc.PEPContext("gd_diff_stepsize").set_as_current()
    pep_builder = pep.PEPBuilder(ctx)
    eta = 1 / pm.Parameter(name="L")
    N = 4

    f = function.SmoothConvexFunction(
        is_basis=True, tags=["f"], L=pm.Parameter(name="L")
    )
    x = pep_builder.add_init_point("x_0")
    x_star = f.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        ((x - x_star) ** 2).le(1, name="initial_condition")
    )

    # We first build the algorithm with the largest number of iterations.
    for i in range(N):
        x = x - eta * f.grad(x)
        x.add_tag(f"x_{i + 1}")
    pep_builder.set_performance_metric(f(x) - f(x_star))

    for l_val in [1, 4, 0.25]:
        result = pep_builder.solve_primal(resolve_parameters={"L": l_val})
        expected_opt_value = l_val / (4 * N + 2)
        assert math.isclose(result.opt_value, expected_opt_value, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual(resolve_parameters={"L": l_val})
        assert math.isclose(dual_result.opt_value, expected_opt_value, rel_tol=1e-3)


def test_pgm_e2e():
    ctx = pc.PEPContext("pgm").set_as_current()
    pep_builder = pep.PEPBuilder(ctx)
    eta = 1
    N = 1

    f = function.SmoothConvexFunction(is_basis=True, tags=["f"], L=1)
    g = function.ConvexFunction(is_basis=True, tags=["g"])

    h = f + g

    x = pep_builder.add_init_point("x_0")
    x_star = h.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        ((x - x_star) ** 2).le(1, name="initial_condition")
    )

    # We first build the algorithm with the largest number of iterations.
    for i in range(N):
        y = x - eta * f.grad(x)
        y.add_tag(f"y_{i + 1}")
        x = g.prox(y, eta, tag=f"x_{i + 1}")

    # To achieve the sweep, we can just update the performance_metric.
    for i in range(1, N + 1):
        p = ctx.get_by_tag(f"x_{i}")
        pep_builder.set_performance_metric(h.func_val(p) - h.func_val(x_star))

        result = pep_builder.solve_primal()
        expected_opt_value = 1 / (4 * i)
        assert math.isclose(result.opt_value, expected_opt_value, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual()
        assert math.isclose(dual_result.opt_value, expected_opt_value, rel_tol=1e-3)


def test_ogm_e2e():
    ogm = pc.PEPContext("ogm").set_as_current()
    pep_builder = pep.PEPBuilder(ogm)

    L = 1
    f = function.SmoothConvexFunction(is_basis=True, tags=["f"], L=1)

    N_range = 10

    theta = [pm.Parameter(f"theta_{i}") for i in range(N_range + 1)]

    @functools.cache
    def theta_ogm(i, N):
        if i == -1:
            return 0
        if i == N:
            return 1 / 2 * (1 + np.sqrt(8 * theta_ogm(N - 1, N) ** 2 + 1))
        return 1 / 2 * (1 + np.sqrt(4 * theta_ogm(i - 1, N) ** 2 + 1))

    x_0 = pep_builder.add_init_point("x_0")
    x = x_0
    z = x_0

    eta = 1 / L

    x_star = f.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        ScalarConstraint.make((x_0 - x_star) ** 2, "<=", 1, name="initial_condition")
    )

    for N in range(1, N_range):
        y = x - eta * f.grad(x)
        z = z - 2 * eta * theta[N - 1] * f.grad(x)
        x = (1 - 1 / theta[N]) * y + 1 / theta[N] * z

        z.add_tag(f"z_{N}")
        x.add_tag(f"x_{N}")

        x_N = ogm.get_by_tag(f"x_{N}")
        pep_builder.set_performance_metric(f(x_N) - f(x_star))

        result = pep_builder.solve_primal(
            resolve_parameters={f"theta_{i}": theta_ogm(i, N) for i in range(N + 1)}
        )
        expected_opt_value_N = L / (2 * theta_ogm(N, N) ** 2)
        assert math.isclose(result.opt_value, expected_opt_value_N, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual(
            resolve_parameters={f"theta_{i}": theta_ogm(i, N) for i in range(N + 1)}
        )
        assert math.isclose(dual_result.opt_value, expected_opt_value_N, rel_tol=1e-3)


def test_ogm_g_e2e():
    ogm_g = pc.PEPContext("ogm_g").set_as_current()
    pep_builder = pep.PEPBuilder(ogm_g)

    L = 1
    f = function.SmoothConvexFunction(is_basis=True, tags=["f"], L=1)

    N_range = 10

    reversed_theta = [pm.Parameter(f"reversed_theta_{i}") for i in range(N_range + 1)]

    @functools.cache
    def theta_ogm(i, N):
        if i == -1:
            return 0
        if i == N:
            return 1 / 2 * (1 + np.sqrt(8 * theta_ogm(N - 1, N) ** 2 + 1))
        return 1 / 2 * (1 + np.sqrt(4 * theta_ogm(i - 1, N) ** 2 + 1))

    def reverse_theta_ogm(i, N):
        return theta_ogm(N - i, N)

    x_0 = pep_builder.add_init_point("x_0")
    x = x_0
    z = x_0

    eta = 1 / L
    z = z - eta * (reversed_theta[0] + 1) / 2 * f.grad(x)
    z.add_tag(f"z_{1}")

    x_star = f.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        ScalarConstraint.make(f(x_0) - f(x_star), "<=", 1, name="initial_condition")
    )

    for N in range(1, N_range):
        y = x - eta * f.grad(x)
        x = (reversed_theta[N + 1] / reversed_theta[N]) ** 4 * y + (
            1 - (reversed_theta[N + 1] / reversed_theta[N]) ** 4
        ) * z
        z = z - eta * reversed_theta[N] * f.grad(x)

        x.add_tag(f"x_{N}")
        z.add_tag(f"z_{N + 1}")

        x_N = ogm_g.get_by_tag(f"x_{N}")
        pep_builder.set_performance_metric((f.grad(x_N)) ** 2)

        result = pep_builder.solve_primal(
            resolve_parameters={
                f"reversed_theta_{i}": reverse_theta_ogm(i, N) for i in range(N + 2)
            }
        )
        expected_opt_value_N = 2 * L / reverse_theta_ogm(0, N) ** 2
        assert math.isclose(result.opt_value, expected_opt_value_N, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual(
            resolve_parameters={
                f"reversed_theta_{i}": reverse_theta_ogm(i, N) for i in range(N + 2)
            }
        )
        assert math.isclose(dual_result.opt_value, expected_opt_value_N, rel_tol=1e-3)


def test_agm_e2e():
    agm = pc.PEPContext("agm").set_as_current()
    pep_builder = pep.PEPBuilder(agm)

    L = 1
    f = function.SmoothConvexFunction(is_basis=True, tags=["f"], L=1)

    N_range = 10

    theta = [pm.Parameter(f"theta_{i}") for i in range(N_range + 1)]

    @functools.cache
    def theta_agm(i):
        if i == -1:
            return 0
        return 1 / 2 * (1 + np.sqrt(4 * theta_agm(i - 1) ** 2 + 1))

    x_0 = pep_builder.add_init_point("x_0")
    x = x_0
    z = x_0

    eta = 1 / L

    x_star = f.set_stationary_point("x_star")
    pep_builder.add_initial_constraint(
        ((x_0 - x_star) ** 2).le(1, name="initial_condition")
    )

    for N in range(1, N_range):
        y = x - eta * f.grad(x)
        z = z - eta * theta[N - 1] * f.grad(x)
        x = (1 - 1 / theta[N]) * y + 1 / theta[N] * z

        z.add_tag(f"z_{N}")
        x.add_tag(f"x_{N}")

        x_N = agm.get_by_tag(f"x_{N}")
        pep_builder.set_performance_metric(f(x_N) - f(x_star))

        # Additional dual constraints.
        pep_builder.dual_val_constraint.clear()

        relaxed_constraints = []
        index_set = list(range(N + 1)) + ["star"]
        for i, j in itertools.product(index_set, index_set):
            if i != j and i != "star" and j != i + 1:
                relaxed_constraints.append(f"f:x_{i},x_{j}")
        pep_builder.set_relaxed_constraints(relaxed_constraints)

        for i in range(N + 1):
            pep_builder.add_dual_val_constraint(
                f"f:x_{i},x_{i + 1}", "==", theta_agm(i) ** 2 / theta_agm(N) ** 2
            )

        # Solve the dual problem with the additional constraints and compare it with the desired convergence rate.
        dual_result = pep_builder.solve_dual(
            resolve_parameters={f"theta_{i}": theta_agm(i) for i in range(N + 1)}
        )

        expected_opt_value_N = L / (2 * theta_agm(N) ** 2)
        assert math.isclose(dual_result.opt_value, expected_opt_value_N, rel_tol=1e-3)


def test_pdhg_e2e():
    pdhg = pc.PEPContext("pdhg").set_as_current()
    pep_builder = pep.PEPBuilder(pdhg)
    alpha = 1.0
    N_range = 2

    # Declare two convex functions.
    f = function.ConvexFunction(is_basis=True, tags=["f"])
    g = function.ConvexFunction(is_basis=True, tags=["g"])

    # Declare a linear operator.
    A = operator.LinearOperator(is_basis=True, tags=["A"], M=1)

    # Declare the initial points.
    x_0 = pep_builder.add_init_point("x_0")
    u_0 = pep_builder.add_init_point("u_0")

    # Declare the points used in the primal-dual gap function.
    x_tilde = vector.Vector(is_basis=True)
    x_tilde.add_tag("x_tilde")
    u_tilde = vector.Vector(is_basis=True)
    u_tilde.add_tag("u_tilde")
    p_avg = vector.Vector(is_basis=True)

    pep_builder.add_initial_constraint(
        ((1.0 / alpha) * (x_0 - x_tilde) ** 2 + alpha * (u_0 - u_tilde) ** 2).le(
            1, name="initial_condition"
        )
    )

    # Define p_tilde such that u_tilde \in \partial g(p_tilde)
    p_tilde = vector.Vector(is_basis=True)
    p_tilde.add_tag("p_tilde")
    g.add_point_with_grad_restriction(p_tilde, u_tilde)

    x_sum = vector.Vector.zero()
    u_sum = vector.Vector.zero()
    x_sum.add_tag("x_sum")
    u_sum.add_tag("u_sum")

    x = x_0
    u = u_0
    for i in range(N_range):
        x_old = x

        x = f.prox(x - alpha * A.T(u), alpha, tag=f"x_{i + 1}")

        t = u + 1 / alpha * (2 * A(x) - A(x_old))
        p = g.prox(alpha * t, alpha, tag=f"p_{i + 1}")
        u = t - 1 / alpha * p
        u.add_tag(f"u_{i + 1}")

        x_sum = x_sum + x
        u_sum = u_sum + u
        x_sum.add_tag(f"x_sum_{i + 1}")
        u_sum.add_tag(f"u_sum_{i + 1}")

    # To achieve the sweep, we can just update the performance_metric.
    for N in range(1, N_range + 1):
        x_avg = pdhg.get_by_tag(f"x_sum_{N}") / float(N)
        u_avg = pdhg.get_by_tag(f"u_sum_{N}") / float(N)

        # Define p_avg such that u_avg \in \partial g(p_avg)
        p_avg.add_tag(f"p_avg_{N}")
        g.add_point_with_grad_restriction(p_avg, u_avg)

        pep_builder.set_performance_metric(
            f(x_avg)
            - f(x_tilde)
            + g(p_tilde)
            - g(p_avg)
            + A.T(u_tilde) * x_avg
            - u_tilde * p_tilde
            - u_avg * A(x_tilde)
            + u_avg * p_avg
        )

        result = pep_builder.solve_primal()
        expected_opt_value = 1 / (N + 1)
        assert math.isclose(result.opt_value, expected_opt_value, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual()
        assert math.isclose(dual_result.opt_value, expected_opt_value, rel_tol=1e-3)

        # Erase the last tag and triplet that are redundant for the next N
        p_avg.tags.pop(-1)
        pdhg.func_to_triplets[g].pop(-1)


def test_drs_e2e():
    drs = pc.PEPContext("drs").set_as_current()
    pep_builder = pep.PEPBuilder(drs)
    alpha = 1.0
    N_range = 2

    # Declare two convex functions.
    f = function.ConvexFunction(is_basis=True, tags=["f"])
    g = function.ConvexFunction(is_basis=True, tags=["g"])

    # Declare the initial points.
    x_0 = pep_builder.add_init_point("x_0")
    u_0 = pep_builder.add_init_point("u_0")

    # Declare the points used in the primal-dual gap function.
    x_tilde = vector.Vector(is_basis=True)
    x_tilde.add_tag("x_tilde")
    u_tilde = vector.Vector(is_basis=True)
    u_tilde.add_tag("u_tilde")
    p_avg = vector.Vector(is_basis=True)

    pep_builder.add_initial_constraint(
        ((1.0 / alpha) * (x_0 - x_tilde) ** 2 + alpha * (u_0 - u_tilde) ** 2).le(
            1, name="initial_condition"
        )
    )

    # Define p_tilde such that u_tilde \in \partial g(p_tilde)
    p_tilde = vector.Vector(is_basis=True)
    p_tilde.add_tag("p_tilde")
    g.add_point_with_grad_restriction(p_tilde, u_tilde)

    x_sum = vector.Vector.zero()
    u_sum = vector.Vector.zero()
    x_sum.add_tag("x_sum")
    u_sum.add_tag("u_sum")

    x = x_0
    u = u_0
    for i in range(N_range):
        x_old = x

        x = f.prox(x - alpha * u, alpha, tag=f"x_{i + 1}")

        t = u + 1 / alpha * (2 * x - x_old)
        p = g.prox(alpha * t, alpha, tag=f"p_{i + 1}")
        u = t - 1 / alpha * p
        u.add_tag(f"u_{i + 1}")

        x_sum = x_sum + x
        u_sum = u_sum + u
        x_sum.add_tag(f"x_sum_{i + 1}")
        u_sum.add_tag(f"u_sum_{i + 1}")

    # To achieve the sweep, we can just update the performance_metric.
    for N in range(1, N_range + 1):
        x_avg = drs.get_by_tag(f"x_sum_{N}") / float(N)
        u_avg = drs.get_by_tag(f"u_sum_{N}") / float(N)

        # Define p_avg such that u_avg \in \partial g(p_avg)
        p_avg.add_tag(f"p_avg_{N}")
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
        expected_opt_value = 1 / (N + 1)
        assert math.isclose(result.opt_value, expected_opt_value, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual()
        assert math.isclose(dual_result.opt_value, expected_opt_value, rel_tol=1e-3)

        # Erase the last tag and triplet that are redundant for the next N
        p_avg.tags.pop(-1)
        drs.func_to_triplets[g].pop(-1)


def test_dys_e2e():
    dys = pc.PEPContext("dys").set_as_current()
    pep_builder = pep.PEPBuilder(dys)
    L = pm.Parameter("L")
    alpha = 1.0 / L
    N_range = 2

    # Declare two convex functions.
    f = function.ConvexFunction(is_basis=True, tags=["f"])
    g = function.ConvexFunction(is_basis=True, tags=["g"])
    h = function.SmoothConvexFunction(is_basis=True, tags=["h"], L=1)

    # Declare the initial points.
    x_0 = pep_builder.add_init_point("x_0")
    u_0 = pep_builder.add_init_point("u_0")

    # Declare the points used in the primal-dual gap function.
    x_tilde = vector.Vector(is_basis=True)
    x_tilde.add_tag("x_tilde")
    u_tilde = vector.Vector(is_basis=True)
    u_tilde.add_tag("u_tilde")
    p_avg = vector.Vector(is_basis=True)

    pep_builder.add_initial_constraint(
        ((1.0 / alpha) * (x_0 - x_tilde) ** 2 + alpha * (u_0 - u_tilde) ** 2).le(
            1, name="initial_condition"
        )
    )

    # Define p_tilde such that u_tilde \in \partial g(p_tilde)
    p_tilde = vector.Vector(is_basis=True)
    p_tilde.add_tag("p_tilde")
    g.add_point_with_grad_restriction(p_tilde, u_tilde)

    x_sum = vector.Vector.zero()
    u_sum = vector.Vector.zero()
    x_sum.add_tag("x_sum")
    u_sum.add_tag("u_sum")

    # Generating the sequences with DYS, using x_0 and u_0 as initial points
    # p^{k+1} = prox_{\alpha g} ( \alpha * u + x^k )
    # u^{k+1} = u^k + 1/\alpha * x^k - 1/\alpha * p^{k+1}
    # x^{k+1} = prox_{\alpha f} ( x^k - \alpha * (2u^{k+1} - u^k) - \alpha \nabla h(p^{k+1}) )
    x = x_0
    u = u_0
    for i in range(N_range):
        u_old = u

        t = u + 1 / alpha * x
        p = g.prox(alpha * t, alpha, tag=f"p_{i + 1}")
        u = (t - 1 / alpha * p).add_tag(f"u_{i + 1}")
        x = f.prox(
            x - alpha * (2 * u - u_old) - alpha * h.grad(p), alpha, tag=f"x_{i + 1}"
        )

        x_sum = x_sum + x
        u_sum = u_sum + u
        x_sum.add_tag(f"x_sum_{i + 1}")
        u_sum.add_tag(f"u_sum_{i + 1}")

    # To achieve the sweep, we can just update the performance_metric.
    for N in range(1, N_range + 1):
        x_avg = dys.get_by_tag(f"x_sum_{N}") / float(N)
        u_avg = dys.get_by_tag(f"u_sum_{N}") / float(N)

        # Define p_avg such that u_avg \in \partial g(p_avg)
        p_avg.add_tag(f"p_avg_{N}")
        g.add_point_with_grad_restriction(p_avg, u_avg)

        pep_builder.set_performance_metric(
            f(x_avg)
            + h(x_avg)
            - f(x_tilde)
            - h(x_tilde)
            + g(p_tilde)
            - g(p_avg)
            + u_tilde * x_avg
            - u_tilde * p_tilde
            - u_avg * x_tilde
            + u_avg * p_avg
        )

        result = pep_builder.solve_primal(resolve_parameters={"L": 1})
        expected_opt_value = 1 / N
        assert math.isclose(result.opt_value, expected_opt_value, rel_tol=1e-2)

        dual_result = pep_builder.solve_dual(resolve_parameters={"L": 1})
        assert math.isclose(dual_result.opt_value, expected_opt_value, rel_tol=1e-2)

        # Erase the last tag and triplet that are redundant for the next N
        p_avg.tags.pop(-1)
        dys.func_to_triplets[g].pop(-1)


def test_appm_e2e():
    appm = pc.PEPContext("appm").set_as_current()
    pep_builder = pep.PEPBuilder(appm)
    alpha = 1
    N_range = 10

    # Declare monotone operator.
    A = operator.MonotoneOperator(is_basis=True, tags=["A"])

    # Declare a parameter used in the algorithm.
    beta = [pm.Parameter(f"beta_{i}") for i in range(N_range + 1)]

    # Define the initial points.
    x_0 = pep_builder.add_init_point("x_0")
    y = x_0

    x_star = A.set_zero_point("x_star")
    pep_builder.add_initial_constraint(
        ((x_0 - x_star) ** 2).le(1, name="initial_condition")
    )

    for N in range(N_range):
        x_next = A.resolvent(y, alpha, tag=f"x_{N + 1}")
        y_next = ((1 - beta[N]) * (2 * x_next - y) + beta[N] * x_0).add_tag(
            f"y_{N + 1}"
        )
        y = y_next

        pep_builder.set_performance_metric(A(x_next) ** 2)

        result = pep_builder.solve_primal(
            resolve_parameters={f"beta_{i}": 1 / (i + 2) for i in range(N + 1)}
        )

        expected_opt_value_N = 1 / (alpha**2 * (N + 1) ** 2)
        assert math.isclose(result.opt_value, expected_opt_value_N, rel_tol=1e-2)

        dual_result = pep_builder.solve_dual(
            resolve_parameters={f"beta_{i}": 1 / (i + 2) for i in range(N + 1)}
        )
        assert math.isclose(dual_result.opt_value, expected_opt_value_N, rel_tol=1e-2)


def test_bppm_e2e():
    ctx = pc.PEPContext("bppm").set_as_current()
    pep_builder = pep.PEPBuilder(ctx)
    alpha = 1
    R = 1
    N = 2

    f = function.ConvexFunction(is_basis=True, tags=["f"])
    h = function.ConvexFunction(is_basis=True, tags=["h"])

    x = vector.Vector(is_basis=True, tags=["x_0"])
    f.set_stationary_point("x_star")

    x_0 = ctx["x_0"]
    x_star = ctx["x_star"]
    pep_builder.add_initial_constraint(
        (h(x_star) - h(x_0) - h.grad(x_0) * (x_star - x_0)).le(
            R, name="initial_condition"
        )
    )

    # We first build the algorithm with the largest number of iterations.
    for i in range(N):
        x = f.bregman_prox(x, alpha, h)
        x.add_tag(f"x_{i + 1}")

    # To achieve the sweep, we can just update the performance_metric.
    for i in range(1, N + 1):
        x_i = ctx[f"x_{i}"]
        pep_builder.set_performance_metric(f(x_i) - f(x_star))

        result = pep_builder.solve_primal()
        expected_opt_value = alpha * R / i
        assert math.isclose(result.opt_value, expected_opt_value, rel_tol=1e-3)

        dual_result = pep_builder.solve_dual()
        assert math.isclose(dual_result.opt_value, expected_opt_value, rel_tol=1e-3)
