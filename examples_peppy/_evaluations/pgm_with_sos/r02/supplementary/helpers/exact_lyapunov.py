"""Exact local Lyapunov identities; each definition is also included in the notebook."""

import sympy as sp

import pepflow as pf


def smooth_residual(F, u, v, L):
    return F(v) - F(u) + F.grad(v) * (u - v) + (F.grad(u) - F.grad(v)) ** 2 / (2 * L)


def convex_residual(G, u, v):
    return G(v) - G(u) + G.grad(v) * (u - v)


def phi(k, N, L, x, star, F, G):
    d = x - star
    a, astar = F.grad(x), F.grad(star)
    return (
        L * (N - k) / (2 * N - k) ** 2 * d**2
        - a * d / (2 * N - k)
        + (a - astar) ** 2 / (2 * L * (2 * N - k))
        + (k + 1) / (2 * N - k) * (F(x) - F(star))
        + k / (2 * N - k) * (G(x) - G(star))
    )


def step_square(i, N, L, x, xplus, star, F, G):
    a0, a1, astar = F.grad(x), F.grad(xplus), F.grad(star)
    s = G.grad(xplus)
    c1 = N / ((2 * N + 1 - i) * (2 * N - i) * L)
    u1 = i / (2 * N) * a1 + (2 * N - i) / (2 * N) * a0 - astar
    c2 = (
        (i - 1) / (2 * N - i) * (2 * N + 2) / (2 * N + 1)
        + 2 * N / ((2 * N - i) ** 2 * (2 * N + 1))
    ) / (2 * L)
    u2 = a0 + s - L / (2 * N + 1 - i) * (x - star)
    c3 = i / (2 * N + 1 - i) * 2 * N / (2 * N + 1) / (2 * L)
    u3 = (
        (2 * N + 1) / (2 * N) * (a1 + s)
        - (a0 + s) / (2 * N)
        - L / (2 * N - i) * (xplus - star)
    )
    return c1 * u1**2 + c2 * u2**2 + c3 * u3**2


def local_context(label, L):
    ctx = pf.PEPContext(label).set_as_current()
    F = pf.SmoothConvexFunction(is_basis=True, tags=[f"f_{{{label}}}"], L=L)
    G = pf.ConvexFunction(is_basis=True, tags=[f"g_{{{label}}}"])
    H = F + G
    star = H.set_stationary_point(f"x_{{star,{label}}}")
    x = pf.Vector(is_basis=True, tags=[f"x_{{{label}}}"])
    xp = G.prox(x - F.grad(x) / L, 1 / L, tag=f"x_{{plus,{label}}}")
    F(xp)
    return ctx, F, G, H, star, x, xp


def exact_components(expression, ctx, parameters):
    manager = pf.ExpressionManager(ctx, resolve_parameters=parameters)
    value = manager.eval_scalar(expression, sympy_mode=True)
    gram = sp.Matrix(value.inner_prod_coords).applyfunc(
        lambda z: sp.factor(sp.cancel(z))
    )
    funcs = sp.Matrix(list(value.func_coords)).applyfunc(
        lambda z: sp.factor(sp.cancel(z))
    )
    offset = sp.factor(sp.cancel(value.offset))
    return gram, funcs, offset


def assert_identity(name, LHS, RHS, ctx, parameters, display=False):
    gram, funcs, offset = exact_components(LHS - RHS, ctx, parameters)
    passed = all(v == 0 for v in [*gram, *funcs, offset])
    print(
        name, "exact zero:", passed, "coordinates:", gram.shape, funcs.shape, flush=True
    )
    if display:
        pf.pprint_labeled_matrix(
            __import__("numpy").array(gram.tolist(), dtype=object),
            [str(v) for v in ctx.basis_vectors()],
        )
        print("Function-coordinate residual:", funcs)
        print("Offset residual:", offset)
    if not passed:
        print(
            "Nonzero entries:",
            [v for v in [*gram, *funcs, offset] if v != 0],
            flush=True,
        )
    assert passed
    return dict(
        passed=passed,
        gram_shape=list(gram.shape),
        function_shape=list(funcs.shape),
        offset=str(offset),
    )
