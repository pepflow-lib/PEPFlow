import sympy as sp
k,n,L=sp.symbols('k n L',positive=True)
u,p,q,r,s=sp.symbols('u p q r s',real=True)
b,c=sp.symbols('b c',real=True)
F,Fp,G,Gp=sp.symbols('F Fp G Gp',real=True)
v=u-(p+q)/L
ak=(k+1)/(2*n-k); ap=(k+2)/(2*n-k-1)
bk=k/(2*n-k); bp=(k+1)/(2*n-k-1)
A=L*(n-k)/(2*n-k)**2; Ap=L*(n-k-1)/(2*n-k-1)**2
Vk=A*u**2-u*(p+s)/(2*n-k)-b*p**2/L+ak*F+bk*G
Vp=Ap*v**2-v*(r+s)/(2*n-k-1)-c*r**2/L+ap*Fp+bp*Gp
Ifstar=Fp-(r+s)*v+r**2/(2*L)
Ifstep=Fp-F+(r+s)*(u-v)+(p-r)**2/(2*L)
Igstar=Gp-(q-s)*v
Igstep=Gp-G+(q-s)*(u-v)
Q=sp.factor((ap-ak)*Ifstar+ak*Ifstep+(bp-bk)*Igstar+bk*Igstep-(Vp-Vk))
print('Q=',sp.collect(sp.expand(Q),[u,s,F,Fp,G,Gp]))
variables=sp.Matrix([u,p,q,r,s])
M=sp.simplify(sp.hessian(Q,variables)/2)
print('M=');sp.print_latex(M)
for i in range(5):
    for j in range(i,5):
        if M[i,j]!=0:print(i,j,sp.factor(M[i,j]))
# eliminate r then q then inspect p/u coefficients
R=sp.simplify(M-M[:,3]*M[3,:]/M[3,3])
T=sp.simplify(R-R[:,2]*R[2,:]/R[2,2])
print('p residual',sp.factor(T[1,1]))
print('recurrence b=',sp.solve(T[1,1],b))
print('r pivot',sp.factor(M[3,3]),'q pivot',sp.factor(R[2,2]))
