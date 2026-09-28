import sympy as sp
exec(compile(open('supplementary/b5_simple_choice.py',encoding='utf-8-sig').read(),'simple','exec'))
d=sp.symbols('d',positive=True)
print('principal PSD checks with t=k+2d:')
for ii in [[3],[2,3],[1,2,3]]:
    determinant=sp.factor(M.extract(ii,ii).det(method='domain-ge'))
    numerator,denominator=sp.fraction(determinant)
    shifted=sp.Poly(sp.expand(numerator.subs(t,k+2*(d+2))),k,d)
    print(ii,'denominator',sp.factor(denominator),'shifted numerator',shifted.as_expr(),'all coefficients >=0',all(c>=0 for c in shifted.coeffs()))

