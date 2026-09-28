# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Exact PEPFlow scalar-coordinate verification, including function values and offsets.
k_sym = sp.Symbol("k", integer=True, nonnegative=True)
N_sym = sp.Symbol("N", integer=True, positive=True)
alpha_sym = sp.Symbol("alpha", positive=True)
R_sym = sp.Symbol("R", nonnegative=True)
k_par, N_par = pf.Parameter("k"), pf.Parameter("N")
alpha_par, R_par = pf.Parameter("alpha"), pf.Parameter("R")
symbolic_params = {"k": k_sym, "N": N_sym, "alpha": alpha_sym, "R": R_sym}
exact_results = {}


def D_of(kernel, u, v):
    return kernel(u) - kernel(v) - kernel.grad(v) * (u - v)


def prox_step(function, x, stepsize, kernel, tag):
    return function.bregman_prox(x, stepsize, kernel, tag=tag)


def symbolic_manager(context, parameters):
    """Use the framework's symbolic substitution mode through its generic API."""
    return pf.ExpressionManager(context, resolve_parameters=parameters)


def exact_check(name, expression, manager, context):
    value = manager.eval_scalar(pf.Scalar.zero() + expression, sympy_mode=True)
    gram = sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    funcs = sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    offset = sp.simplify(sp.sympify(value.offset))
    assert all(term == 0 for term in [*gram, *funcs, offset]), name
    print(name + ": exact Gram, function, and offset residuals are zero.")
    pf.pprint_labeled_matrix(
        pf.MatrixWithNames(
            np.asarray(gram, dtype=object),
            [str(v) for v in context.basis_vectors()],
            [str(v) for v in context.basis_vectors()],
        )
    )
    pf.pprint_labeled_matrix(
        pf.MatrixWithNames(
            np.asarray(funcs, dtype=object).reshape(1, -1),
            ["function residual"],
            [str(v) for v in context.basis_scalars()],
        )
    )
    print("Constant residual:", offset)
    exact_results[name] = {
        "gram_zero": True,
        "function_zero": True,
        "offset_zero": True,
        "gram_shape": list(gram.shape),
        "function_count": len(funcs),
    }
    return True
