import sympy as sp
k,N,Z,W=sp.symbols('k N Z W',real=True)
u,p,q,r,s=sp.symbols('u p q r s',real=True)
F,G,H,J=sp.symbols('F G H J',real=True)
def coeff(k,z):
    m=2*N-k
    a=(k+1)/m;b=k/m
    A=(N-k-1+(k+1)/(2*m)-z)/(m-1)**2
    B=1/(2*m)+z/(m-1)
    C=-(k-1)/(2*m)-z
    return a,b,A,B,C
def V(k,z,xnext,p,q,F,G):
    a,b,A,B,C=coeff(k,z)
    return a*F+b*G-a*p*p/2-b*p*q+A*xnext*xnext+2*B*xnext*q+C*q*q
a,b,*_=coeff(k,Z)
an,bn,*_=coeff(k+1,W)
If=H-F+r*(p+q)+(r-p)**2/2
Ifs=H-r*u+r*r/2
Ig=J-G+q*(p+q)
Igs=J-q*u
T=a*If+(an-a)*Ifs+b*Ig+(bn-b)*Igs
S=sp.factor(T-(V(k+1,W,u-r-s,r,s,H,J)-V(k,Z,u,p,q,F,G)))
print('free symbols',S.free_symbols,flush=True)
M=sp.hessian(S,(u,q,r,s))/2
M=M.applyfunc(sp.factor)
print('M',M,flush=True)
# Reverse-eliminate s then r, as in the numerical recipe.
M3=(M[:3,:3]-M[:3,3]*M[3,:3]/M[3,3]).applyfunc(sp.factor)
M2=(M3[:2,:2]-M3[:2,2]*M3[2,:2]/M3[2,2]).applyfunc(sp.factor)
print('pivot s',sp.factor(M[3,3]),flush=True)
print('pivot r',sp.factor(M3[2,2]),flush=True)
print('residual',M2,flush=True)
sol=sp.solve(M2[1,1],Z)[0]
print('recurrence Z=',sp.factor(sol),flush=True)
print('residual sub',M2.subs(Z,sol).applyfunc(sp.factor),flush=True)
from pathlib import Path
Path('supplementary/b5-recurrence.txt').write_text(str(sp.factor(sol)))
