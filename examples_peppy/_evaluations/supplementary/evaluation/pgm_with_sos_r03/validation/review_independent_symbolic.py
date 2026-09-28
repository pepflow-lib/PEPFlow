import json
from pathlib import Path
import sympy as s
N,k,L=s.symbols('N k L', positive=True)
x,d0,a,b,z,t=s.symbols('x d0 a b astar subgradient')
fx,fy,gx,gy=s.symbols('fx fy gx gy')
y=x-(a+t)/L
Ifxy=fy-fx+b*(x-y)+(a-b)**2/(2*L)
Ifsy=fy-b*y+(z-b)**2/(2*L)
Ifsx=fx-a*x+(z-a)**2/(2*L)
Igxy=gy-gx+t*(x-y)
Igsy=gy-t*y

def V(d,aa,f,g,j):
    return -L*d0**2/(4*N)+L*(N-j)*d**2/(2*N-j)**2-d*aa/(2*N-j)+(aa-z)**2/(2*L*(2*N-j))+(j+1)*f/(2*N-j)+j*g/(2*N-j)
def Q(i):
    c1=N/((2*N+1-i)*(2*N-i)*L)
    u1=i*b/(2*N)+(2*N-i)*a/(2*N)-z
    c2=((i-1)*(2*N+2)/((2*N-i)*(2*N+1))+2*N/((2*N-i)**2*(2*N+1)))/(2*L)
    u2=a+t-L*x/(2*N+1-i)
    c3=i*2*N/((2*N+1-i)*(2*N+1)*2*L)
    u3=(2*N+1)*(b+t)/(2*N)-(a+t)/(2*N)-L*y/(2*N-i)
    return c1*u1**2+c2*u2**2+c3*u3**2
interior_rhs=(k+1)/(2*N-k)*Ifxy+k/(2*N-k)*Igxy+(2*N+1)/((2*N-k-1)*(2*N-k))*Ifsy+2*N/((2*N-k-1)*(2*N-k))*Igsy-Q(k+1)
base_rhs=Ifsx/(2*N)+(2*N+1)*Ifsy/((2*N-1)*2*N)+Ifxy/(2*N)+Igsy/(2*N-1)-Q(1)
terminal=fy+gy-L*d0**2/(4*N)
terminal_rhs=Ifsy/(N+1)+2*Igsy/(N+1)+N*Ifxy/(N+1)+(N-1)*Igxy/(N+1)-Q(N)
single_rhs=(Ifsx+Ifsy+Ifxy)/2+Igsy-Q(1)
checks={'interior':V(y,b,fy,gy,k+1)-V(x,a,fx,gx,k)-interior_rhs,'base':(V(y,b,fy,gy,1)-base_rhs).subs(d0,x),'terminal':terminal-V(x,a,fx,gx,N-1)-terminal_rhs,'N1':(terminal-single_rhs).subs({N:1,d0:x})}
results={name:str(s.factor(expr)) for name,expr in checks.items()}
assert set(results.values())=={'0'},results
results['method']='Independent commutative polynomial expansion of submitted quadratic/dot-product expressions in one arbitrary coordinate, plus independent formal function-value gaps; substitute y=x-(a+s)/L and x_star=0. Vanishing quadratic polynomial coefficients verify the Euclidean identities coordinatewise.'
Path('review-independent-symbolic.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
