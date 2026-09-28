# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def exact_components(expression, manager):
    value = manager.eval_scalar(pf.Scalar.zero() + expression, sympy_mode=True)
    gram = sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    function = sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    offset = sp.simplify(sp.sympify(value.offset))
    return gram, function, offset


def verify_exact(name, expression, manager, context):
    gram, function, offset = exact_components(expression, manager)
    labels = [str(v) for v in context.basis_vectors()]
    pf.pprint_labeled_matrix(
        pf.MatrixWithNames(np.asarray(gram, dtype=object), labels, labels)
    )
    print(name, "function residual:", function, "constant residual:", offset)
    assert all(term == 0 for term in [*gram, *function, offset]), name
    print(name, "all components exactly zero")
    return True
