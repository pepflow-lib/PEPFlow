import sympy as sp
n,k=sp.symbols('n k',integer=True,positive=True)
d,p,q,z,s=sp.symbols('d p q z s',real=True)
t,u=sp.symbols('t u',real=True)
y=d-p-q
a=lambda j:(j+1)/(2*n-j)
b=lambda j:j/(2*n-j)
c=lambda j:(n-j)/(2*n-j)**2
v=lambda j,dd,pp,tt:c(j)*dd**2-dd*(pp+s)/(2*n-j)-tt*pp**2
Ifs=-(z+s)*y+z**2/2
Ifk=(z+s)*(d-y)+(z-p)**2/2
Igs=-(q-s)*y
Igk=(q-s)*(d-y)
Q=sp.factor((a(k+1)-a(k))*Ifs+a(k)*Ifk+(b(k+1)-b(k))*Igs+b(k)*Igk-v(k+1,y,z,u)+v(k,d,p,t))
coords=[z,q,d,p]
M=sp.hessian(Q,coords)/2
M=M.applyfunc(sp.factor)
print('M',M)
# eliminate z, then q, exact Schur complements
r=M
for j in range(2):
    pivot=sp.factor(r[0,0]); row=r[0,:]
    print('pivot',j,pivot)
    print('square vector', [sp.factor(x/pivot) for x in row])
    r=(r[1:,1:]-r[1:,0]*r[0,1:]/pivot).applyfunc(sp.factor)
print('remainder',r)
print('t solution',sp.solve(r[1,1],t))
