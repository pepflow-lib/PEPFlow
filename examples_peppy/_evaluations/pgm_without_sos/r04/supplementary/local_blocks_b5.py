from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import sympy as s
k,t,B,C,N=s.symbols('k t B C N')
e,p,q,r=s.symbols('e p q r')
a=(k+1)/t; b=k/t; an=(k+2)/(t-1); bn=(k+1)/(t-1)
A=(t-k)/(2*t*t); An=(t-k-2)/(2*(t-1)**2)
ep=e-p-q
V=A*e*e-e*p/t-B*p*p
Vn=An*ep*ep-ep*r/(t-1)-C*r*r
I=(an-a)*(-r*ep+r*r/2)+a*(r*(e-ep)+(p-r)**2/2)+(bn-b)*(-q*ep)+b*q*(e-ep)
M=(s.hessian(I-Vn+V,[r,q,e,p])/2).applyfunc(s.factor)
print('H',M[:2,:2]); print('K',M[:2,2:]); print('T',M[2:,2:])
# Terminal formula uses an=bn=1 and no terminal quadratic term.
a=(N)/(N+1);b=(N-1)/(N+1);A=1/(N+1)**2;B=(N-1)/(2*(N+1)**2)
Q=(1-a)*(-r*ep+r*r/2)+a*(r*(e-ep)+(p-r)**2/2)+(1-b)*(-q*ep)+b*q*(e-ep)+A*e*e-e*p/(N+1)-B*p*p
M=(s.hessian(Q,[r,q,e,p])/2).applyfunc(s.factor)
H=M[:2,:2];K=M[:2,2:]
print('terminal H',H,'K',K)
print('terminal schur',(M[2:,2:]-K.T*H.inv()*K).applyfunc(s.factor))
