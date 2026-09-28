from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import sympy as s

k,N,B,C=s.symbols('k N B C',integer=True)
e,p,q,r=s.symbols('e p q r')
t=2*N-k
an=(k+2)/(t-1); a=(k+1)/t
bn=(k+1)/(t-1); b=k/t
A=(N-k)/t**2; An=(N-k-1)/(t-1)**2
d=1/t; dn=1/(t-1)
ep=e-p-q
V=A*e**2-d*e*p-B*p**2
Vn=An*ep**2-dn*ep*r-C*r**2
I=(an-a)*(-r*ep+r*r/2)+a*(r*(e-ep)+(p-r)**2/2)+(bn-b)*(-q*ep)+b*q*(e-ep)
Q=s.expand(I-(Vn-V))
M=s.simplify(s.hessian(Q,[r,q,e,p])/2)
H=M[:2,:2]
K=M[:2,2:]
T=s.simplify(M[2:,2:]-K.T*H.inv()*K)
print('H',H.applyfunc(s.factor))
print('Schur',T.applyfunc(s.factor))
sol=s.solve(T[1,1],B)[0]
print('beta recurrence=',s.factor(sol))
print('denom',s.factor(s.denom(sol)))
for nv in [4,6]:
    beta=s.Rational(nv-1, 2*(nv+1)**2)
    vals={nv:s.S.Zero,nv-1:beta}
    for j in range(nv-2,0,-1):
        beta=s.factor(sol.subs({N:nv,k:j,C:beta}))
        vals[j]=beta
    print(nv,vals)
(runtime.ATTEMPT/'supplementary/b5-recurrence.txt').write_text(str(s.factor(sol)))

