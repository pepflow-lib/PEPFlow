import sympy as sp
N,Z=sp.symbols('N Z',real=True)
d,p,q,r,s=sp.symbols('d p q r s',real=True)
F0,F1,G1=sp.symbols('F0 F1 G1',real=True)
m=2*N-1
a=2/m;b=1/m
A=(N-2+1/m-Z)/(m-1)**2
B=1/(2*m)+Z/(m-1)
C=-Z
u=d-p-q
v=u-r-s
V1=-d*d/(4*N)+a*F1+b*G1-a*r*r/2-b*r*s+A*v*v+2*B*v*s+C*s*s
If0=F0-p*d+p*p/2
If1=F1-r*u+r*r/2
If01=F1-F0+r*(p+q)+(r-p)**2/2
Ig1=G1-q*u
T=If0/(2*N)+(a-1/(2*N))*If1+If01/(2*N)+b*Ig1
S=sp.factor(T-V1)
M=(sp.hessian(S,(d,p,q,r,s))/2).applyfunc(sp.factor)
print('base matrix',M,flush=True)
for index in (4,3,2,1):
    pivot=sp.factor(M[index,index])
    print('pivot',index,pivot,flush=True)
    M=(M-M[:,index]*M[index,:]/pivot).applyfunc(sp.factor)
print('residual',M,flush=True)
