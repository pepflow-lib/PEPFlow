import sympy as sp

b4 = json.loads((notebook_dir/'state/bppm_b4.json').read_text())
assert b4['certificate_id'] == certificate['certificate_id']
assert b4['numerical_reconstruction']['certificate_id'] == certificate['certificate_id']
# The preceding visible B3/B4 cells just revalidated the unchanged snapshot.
assert certificate_checked and grouping_checked
assert set(component_residuals) == {str(k) for k in range(N_int+1)}
assert all(max(v.values()) <= 1e-4 for v in component_residuals.values())
proof_checks = {name:False for name in ('step','base','boundary','signs','domain','normalization')}
exact_residuals = {}
a_sym = sp.Symbol('alpha', positive=True)
n_sym = sp.Symbol('N', integer=True, positive=True)
k_sym = sp.Symbol('k', integer=True, nonnegative=True)
r_sym = sp.Symbol('R', nonnegative=True)
a_par, n_par, k_par, r_par = (pf.Parameter(name) for name in ('alpha_exact','N_exact','k_exact','R_exact'))
exact_parameters = {'alpha_exact':a_sym,'N_exact':n_sym,'k_exact':k_sym,'R_exact':r_sym}


def divergence(h_function,u,v):
    return h_function(u)-h_function(v)-h_function.grad(v)*(u-v)


def convex_residual(q,u,v):
    return q(v)-q(u)+q.grad(v)*(u-v)


def verify_exact(name,expression,context):
    manager=pf.ExpressionManager(context,resolve_parameters=cast(dict[str, pf.NUMERICAL_TYPE], exact_parameters))
    value=manager.eval_scalar(pf.Scalar.zero()+expression,sympy_mode=True)
    gram=sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    functions=sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    offset=sp.simplify(sp.sympify(value.offset))
    labels=[str(v) for v in context.basis_vectors()]
    print(name, 'Gram residual:')
    pf.pprint_labeled_matrix(pf.MatrixWithNames(np.array(gram.tolist(),dtype=object),labels,labels))
    print(name, 'function residual:',list(functions))
    print(name, 'constant residual:',offset)
    assert all(v==0 for v in [*gram,*functions,offset]),name
    exact_residuals[name]={'gram_zero':True,'function_zero':True,'offset_zero':True}
    return True
