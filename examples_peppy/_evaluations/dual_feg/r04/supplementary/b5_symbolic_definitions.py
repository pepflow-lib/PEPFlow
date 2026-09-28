# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from typing import Any

b4 = json.loads((notebook_dir / "state/dual_feg_b4.json").read_text())
assert b4["certificate_id"] == b3["certificate_id"]
assert b4["numerical_reconstruction"]["certificate_id"] == b4["certificate_id"]
assert b4["numerical_reconstruction"]["passed"]
proof_checks = {
    name: False
    for name in ("step", "base", "boundary", "signs", "domain", "normalization")
}
exact_identity_results = {}
L_symbol = sp.Symbol("L", positive=True)
N_symbol = sp.Symbol("N", integer=True, positive=True)
t_symbol = sp.Symbol("t", integer=True, positive=True)
R_symbol = sp.Symbol("R", nonnegative=True)
Lp, Np, tp, Rp = (
    pf.Parameter(name) for name in ("L_exact", "N_exact", "t_exact", "R_exact")
)
# The framework's symbolic mode accepts symbolic parameter maps at runtime.
symbolic_values: dict[str, Any] = {
    "L_exact": L_symbol,
    "N_exact": N_symbol,
    "t_exact": t_symbol,
    "R_exact": R_symbol,
}


def potential_exact(t, x, z, g, x0, xN, lipschitz, horizon):
    a, b = x0 - xN, x - xN
    return (
        -4 * lipschitz / horizon * (g * a)
        + 4 * lipschitz / t * (g * b)
        - 4 * (g * z)
        + 4 * lipschitz / t * (b * z)
        - 2 * (z**2)
    )


def terminal_exact(g, x0, xN, lipschitz, horizon):
    return 2 * (g**2) - 4 * lipschitz / horizon * (g * (x0 - xN))


def exact_components(expression, manager):
    value = manager.eval_scalar(pf.Scalar.zero() + expression, sympy_mode=True)
    gram = sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    functions = sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    offset = sp.simplify(sp.sympify(value.offset))
    return gram, functions, offset


def verify_exact(name, expression, manager, context):
    gram, functions, offset = exact_components(expression, manager)
    is_zero = all(value == 0 for value in [*gram, *functions, offset])
    labels = [str(v) for v in context.basis_vectors()]
    pf.pprint_labeled_matrix(
        pf.MatrixWithNames(np.asarray(gram, dtype=object), labels, labels)
    )
    print(
        name,
        "function coordinates:",
        list(functions),
        "offset:",
        offset,
        "all components exactly zero:",
        is_zero,
    )
    assert is_zero, name
    exact_identity_results[name] = {
        "gram_zero": True,
        "function_zero": True,
        "offset_zero": True,
        "gram_shape": list(gram.shape),
    }
    return is_zero
