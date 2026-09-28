import sympy as sp
from typing import Any

k_symbol = sp.Symbol('k',integer=True,nonnegative=True)
N_symbol = sp.Symbol('N',integer=True,positive=True)
alpha_symbol = sp.Symbol('alpha',positive=True)
R_symbol = sp.Symbol('R',nonnegative=True)
k_parameter = pf.Parameter('k')
N_parameter = pf.Parameter('N')
alpha_parameter = pf.Parameter('alpha')
R_parameter = pf.Parameter('R')
symbolic_parameters: dict[str, Any]={'k':k_symbol,'N':N_symbol,'alpha':alpha_symbol,'R':R_symbol}


def bregman(kernel,u,v):
    return kernel(u)-kernel(v)-kernel.grad(v)*(u-v)


def symbolic_components(expression,manager):
    value=manager.eval_scalar(pf.Scalar.zero()+expression,sympy_mode=True)
    gram=sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    functions=sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    offset=sp.simplify(sp.sympify(value.offset))
    return gram,functions,offset


def exact_check(name,LHS,RHS,manager,context):
    diff=LHS-RHS
    gram,functions,offset=symbolic_components(diff,manager)
    assert all(term==0 for term in [*gram,*functions,offset]),(name,gram,functions,offset)
    print(name+' Gram residual:')
    pf.pprint_labeled_matrix(np.asarray(gram.tolist(),dtype=object),[str(v) for v in context.basis_vectors()])
    print(name+' function residual:',functions)
    print(name+' offset residual:',offset)
    return {'gram_exact_zero':True,'function_exact_zero':True,'offset_exact_zero':True}

