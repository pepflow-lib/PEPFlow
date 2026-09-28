from typing import cast
b4=json.loads((notebook_dir/'state/dual_feg_b4.json').read_text())
assert b4['certificate_id']==certificate['certificate_id']
assert b4['numerical_reconstruction']['required_indices']==list(range(N_int+1))
for k,C in coeff_by_k.items():
    assert np.allclose(C,np.asarray(b4['coeff_by_k'][str(k)]).reshape(C.shape),atol=1e-4,rtol=1e-5)
proof_checks={name:False for name in ('step','base','boundary','signs','domain','normalization')}
exact_residuals={}

def potential(t,x,z,X,x0,G,Lp,Np):
    return -4*(G*z)-2*z**2+(4*Lp/t)*((G+z)*(x-X))+(4*Lp/Np)*(G*(X-x0))

def terminal_potential(X,x0,G,Lp,Np):
    return 2*G**2+(4*Lp/Np)*(G*(X-x0))

def symbolic_components(expression,manager):
    value=manager.eval_scalar(pf.Scalar.zero()+expression,sympy_mode=True)
    gram=sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    functions=sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    offset=sp.simplify(sp.sympify(value.offset))
    return gram,functions,offset

def verify_exact(name,expression,manager):
    gram,functions,offset=symbolic_components(expression,manager)
    assert all(v==0 for v in [*gram,*functions,offset]),name
    labels=[str(v) for v in manager.context.basis_vectors()] if hasattr(manager,'context') else [str(i) for i in range(gram.rows)]
    pf.pprint_labeled_matrix(np.array(gram,dtype=object),row_labels=labels)
    print(name,'function residual:',functions,'offset residual:',offset,'exact zero:',True)
    exact_residuals[name]={'gram_zero':True,'function_zero':True,'offset_zero':True,'gram_shape':list(gram.shape)}
    return True
