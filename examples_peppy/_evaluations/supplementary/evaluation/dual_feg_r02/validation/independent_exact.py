import sympy as s,json
from pathlib import Path
x,z,X,x0,g,h,G,star=s.symbols('x z X x0 g h G star', real=True)
t,N,L,R=s.symbols('t N L R',nonzero=True)
def phi(t,x,z,X,x0,G,L,N):return -4*G*z-2*z*z+4*L/t*(G+z)*(x-X)+4*L/N*G*(X-x0)
def terminal(X,x0,G,L,N):return 2*G*G+4*L/N*G*(X-x0)
y=x-(z+g)/L
xn=y-(t-1)/t*(h-g)/L;zn=(t-1)/t*z-h/t
checks={}
checks['step']=s.factor(phi(t-1,xn,zn,X,x0,G,L,N)-phi(t,x,z,X,x0,G,L,N)-2/t**2*((g-h)**2-L**2*(x-y)**2)-4*L/(t*(t-1))*(-(G-h)*(X-y)))
checks['base']=s.factor(phi(N,x0,0,X,x0,G,L,N))
XF=x-(z+g)/L
checks['final_step']=s.factor(terminal(XF,x0,G,L,N)-phi(1,x,z,XF,x0,G,L,N)-2*((g-G)**2-L**2*(x-XF)**2))
X1=x0-g/L
checks['N1']=s.factor(terminal(X1,x0,G,L,1)-2*((g-G)**2-L**2*(x0-X1)**2))
checks['boundary']=s.factor(G**2-4*L**2*R**2/N**2-(terminal(X,x0,G,L,N)-4*L/N*G*(X-star)-(2*L/N*(x0-star)-G)**2+4*L**2/N**2*((x0-star)**2-R**2)))
assert all(v==0 for v in checks.values())
Path('independent-exact.json').write_text(json.dumps({'method':'Independent scalar quadratic polynomial expansion. Coefficient cancellation implies the same Euclidean inner-product identities in every dimension; no cross-coordinate terms occur.','residuals':{k:str(v) for k,v in checks.items()}},indent=2))
print(checks)
