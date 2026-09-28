import sympy as sp
k,t,L=sp.symbols('k t L',positive=True)
u,p,q,r,s=sp.symbols('u p q r s',real=True)
F,Fp,G,Gp=sp.symbols('F Fp G Gp',real=True)
v=u-(p+q)/L
ak=(k+1)/t; ap=(k+2)/(t-1)
bk=k/t; bp=(k+1)/(t-1)
A=L*(t-k)/(2*t**2); Ap=L*(t-k-2)/(2*(t-1)**2)
b=k*(t-k)/(4*t**2); c=(k+1)*(t-k-2)/(4*(t-1)**2)
Vk=A*u**2-u*(p+s)/t-b*p**2/L+ak*F+bk*G
Vp=Ap*v**2-v*(r+s)/(t-1)-c*r**2/L+ap*Fp+bp*Gp
Ifstar=Fp-(r+s)*v+r**2/(2*L)
Ifstep=Fp-F+(r+s)*(u-v)+(p-r)**2/(2*L)
Igstar=Gp-(q-s)*v
Igstep=Gp-G+(q-s)*(u-v)
Q=(ap-ak)*Ifstar+ak*Ifstep+(bp-bk)*Igstar+bk*Igstep-(Vp-Vk)
variables=[u,p,q,r]
M=sp.Matrix(4,4,lambda i,j:sp.factor(sp.diff(Q,variables[i],variables[j])/2))
print('M entries',flush=True)
for i in range(4):
    for j in range(i,4):print(i,j,M[i,j],flush=True)
R=M.copy()
for i in [3,2,1,0]:
    pivot=sp.factor(R[i,i]);print('pivot',i,pivot,flush=True)
    if pivot==0:continue
    row=[sp.factor(R[i,j]/pivot) for j in range(4)]
    print('factor',row,flush=True)
    R=sp.Matrix(4,4,lambda a,b:sp.factor(R[a,b]-pivot*row[a]*row[b]))
