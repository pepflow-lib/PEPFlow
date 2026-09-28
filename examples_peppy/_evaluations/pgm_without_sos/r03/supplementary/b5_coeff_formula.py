import sympy as sp

def transfer_matrix(j,n):
    m=2*n-j
    return sp.Matrix([[j*(j+1)*m*(m-1), j*(j+1)*(m-1)**2*(j+m+1)],[(2*j+1)*m-j, (m-1)*(j*(j+3)*m+m+1)]])

def T_exact(k,n):
    if n<1 or not 0<=k<=n-1:
        raise ValueError('Require N>=1 and 0<=k<N')
    vector=sp.Matrix([n-1,1])
    for j in reversed(range(k,n-1)):
        vector=transfer_matrix(j,n)*vector
    return sp.cancel(vector[0]/vector[1])

k_sym,m_sym,U_sym=sp.symbols('k m U',nonnegative=True)
H_sym=U_sym+(k_sym+2)*(m_sym-1)
D_sym=((2*k_sym+1)*m_sym-k_sym)*U_sym+(m_sym-1)*(k_sym*(k_sym+3)*m_sym+m_sym+1)
T_recurrence=k_sym*(k_sym+1)*(m_sym-1)*(m_sym*U_sym+(m_sym-1)*(k_sym+m_sym+1))/D_sym
r_sym=(k_sym+1)*(m_sym-1)/H_sym
c_sym=(m_sym*H_sym*(k_sym*m_sym+1)-(k_sym+1)**2*(m_sym-1)**2)/(m_sym*D_sym)
A_sym=H_sym/(2*(m_sym-1)**2)
B_sym=D_sym/(2*(m_sym-1)**2*H_sym)
print('Exact finite-product T samples:',{n:[str(T_exact(k,n)) for k in range(n)] for n in (1,4,6)})
assert T_exact(0,1)==0
for n in (4,6):
    for k in range(n-1):
        assert sp.cancel(T_exact(k,n)-T_recurrence.subs({k_sym:k,m_sym:2*n-k,U_sym:T_exact(k+1,n)}))==0
print('Finite-product recurrence sample checks passed; symbolic product splitting supplies the all-horizon recurrence.')
