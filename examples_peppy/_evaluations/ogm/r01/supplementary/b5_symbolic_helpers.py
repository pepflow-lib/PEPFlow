import sympy as sp

ell_sym,t_sym,s_sym,T_sym=sp.symbols('L t s T',positive=True)
R_sym=sp.symbols('R',nonnegative=True)
L_proof=pf.Parameter('L_proof')
t_proof=pf.Parameter('t_proof')
s_proof=pf.Parameter('s_proof')


def interpolation_residual(fun,u,v):
    return fun(v)-fun(u)+fun.grad(v)*(u-v)+(fun.grad(u)-fun.grad(v))**2/(2*L_proof)


def exact_components(expression,manager,relation=None):
    value=manager.eval_scalar(pf.Scalar.zero()+expression,sympy_mode=True)
    def reduce_entry(entry):
        entry=sp.cancel(sp.sympify(entry))
        if relation is not None:
            numerator,denominator=sp.fraction(entry)
            entry=sp.cancel(sp.rem(numerator,relation,t_sym)/denominator)
        return sp.simplify(entry)
    gram=sp.Matrix(value.inner_prod_coords).applyfunc(reduce_entry)
    functions=sp.Matrix(list(value.func_coords)).applyfunc(reduce_entry)
    offset=reduce_entry(value.offset)
    return gram,functions,offset


def assert_exact(name,expression,manager,context,relation=None):
    gram,functions,offset=exact_components(expression,manager,relation)
    assert all(entry==0 for entry in [*gram,*functions,offset]),(name,gram,functions,offset)
    print(name,'Gram residual:')
    pf.pprint_labeled_matrix(np.array(gram.tolist(),dtype=object),[str(v) for v in context.basis_vectors()],precision=0)
    print(name,'function residual:',functions.T)
    print(name,'offset residual:',offset)
    return {'gram_zero':True,'function_zero':True,'offset_zero':True}


symbolic_results={}

