from typing import Any
import sympy as sp
b4=json.loads((NOTEBOOK_DIR/'state/pgm_b4.json').read_text())
assert b4['numerical_reconstruction']['certificate_id']==b4['certificate_id']==b3['certificate_id']
assert all(component_residuals[str(k)][part]<1e-4 for k in range(N_int+1) for part in ('gram','function','offset'))
print('B4 coherent structure rechecked by the preceding executed cells.')

def P(name):
    return pf.Parameter(name)

def exact_components(expression,manager):
    value=manager.eval_scalar(pf.Scalar.zero()+expression,sympy_mode=True)
    return (sp.Matrix(value.inner_prod_coords).applyfunc(sp.factor),sp.Matrix(value.func_coords).applyfunc(sp.factor),sp.factor(value.offset))

def exact_check(label,expression,manager,context):
    gram,functions,offset=exact_components(expression,manager)
    pf.pprint_labeled_matrix(np.asarray(gram,dtype=object),[str(v) for v in context.basis_vectors()],precision=6)
    print(label+' function residual:',functions)
    print(label+' offset residual:',offset)
    assert all(v==0 for v in gram) and all(v==0 for v in functions) and offset==0
    print(label+': exact identity verified')
    return True

N_symbol,k_symbol=sp.symbols('N k',integer=True,positive=True)
L_symbol=sp.symbols('L',positive=True)
U_symbol=sp.symbols('U',nonnegative=True)

def local_coefficients(k,n,U):
    m=2*n-k
    H=U+(k+2)*(m-1)
    D=((2*k+1)*m-k)*U+(m-1)*(k*(k+3)*m+m+1)
    T=k*(k+1)*(m-1)*(m*U+(m-1)*(k+m+1))/D
    r=(k+1)*(m-1)/H
    c=(m*H*(k*m+1)-(k+1)**2*(m-1)**2)/(m*D)
    A=H/(2*(m-1)**2)
    B=D/(2*(m-1)**2*H)
    return m,H,D,T,r,c,A,B

# Exact coefficient-equation derivation in a reduced one-step quadratic model.
kd,md,ud,td=sp.symbols('k m U T',real=True)
dd,pp,qq,zz,ss=sp.symbols('d p q z s',real=True)
nd=(md+kd)/2
yd=dd-pp-qq
ac=(kd+1)/md
bc=kd/md
an=(kd+2)/(md-1)
bn=(kd+1)/(md-1)
vcur=(nd-kd)*dd**2/md**2-dd*(pp+ss)/md-td*pp**2/(2*md**2)
vnext=(nd-kd-1)*yd**2/(md-1)**2-yd*(zz+ss)/(md-1)-ud*zz**2/(2*(md-1)**2)
weighted_q=(an-ac)*(-(zz+ss)*yd+zz**2/2)+ac*((zz+ss)*(dd-yd)+(zz-pp)**2/2)+(bn-bc)*(-(qq-ss)*yd)+bc*(qq-ss)*(dd-yd)
Q_polynomial=sp.factor(weighted_q-vnext+vcur)
_,Hd,Dd,Td,rd,cd,Ad,Bd=local_coefficients(kd,nd,ud)
wpoly=qq-dd/md
square_polynomial=Ad*(zz+rd*(wpoly+pp/md))**2+Bd*(wpoly+cd*pp)**2
recurrence_residual=sp.factor(Q_polynomial.subs(td,Td)-square_polynomial)
assert recurrence_residual==0
assert sp.factor(Td-T_recurrence.subs({k_sym:kd,m_sym:md,U_sym:ud}))==0
print('Coefficient equations solved: exact quadratic residual after T recurrence =',recurrence_residual)
# The finite product splits into its first matrix and its tail; verify its ratio law symbolically.
tail_den=sp.symbols('tail_den',positive=True)
transfer=transfer_matrix(kd,nd)
ratio_vector=transfer*sp.Matrix([ud*tail_den,tail_den])
assert sp.factor(ratio_vector[0]/ratio_vector[1]-Td)==0
print('Exact transfer-product ratio law verified; empty product gives T_(N-1)=N-1, and the j=0 row gives T_0=0.')
