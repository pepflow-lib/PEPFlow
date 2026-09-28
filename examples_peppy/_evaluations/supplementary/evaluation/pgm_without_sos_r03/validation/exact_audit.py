"""Independent expansion of the submitted identities, without solving for coefficients."""
import os
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parent
for key in ('TEMP','TMP','TMPDIR','XDG_CACHE_HOME','MPLCONFIGDIR','IPYTHONDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR'):
    loc = ROOT / 'runtime' / key
    loc.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(loc)
import sympy as s
k,N,L,U=s.symbols('k N L U')
d,p,z,q,t,F,G,F1,G1=s.symbols('d p z q t F G F1 G1')
y=d-p-q
m=2*N-k
H=U+(k+2)*(m-1)
D=((2*k+1)*m-k)*U+(m-1)*(k*(k+3)*m+m+1)
T=k*(k+1)*(m-1)*(m*U+(m-1)*(k+m+1))/D
r=(k+1)*(m-1)/H
c=(m*H*(k*m+1)-(k+1)**2*(m-1)**2)/(m*D)
A=H/(2*(m-1)**2)
B=D/(2*(m-1)**2*H)
w=q-d/m
Q=L*A*(z+r*(w+p/m))**2+L*B*(w+c*p)**2
If0=F-(L*p+t)*d+L*p**2/2
If1=F1-(L*z+t)*y+L*z**2/2
If01=F1-F+(L*z+t)*(d-y)+L*(p-z)**2/2
Ig1=G1-(L*q-t)*y
Ig01=G1-G+(L*q-t)*(d-y)
a=(k+1)/m
b=k/m
an=(k+2)/(m-1)
bn=(k+1)/(m-1)
V=L*(N-k)/m**2*d**2-d*(L*p+t)/m-L*T*p**2/(2*m**2)+a*F+b*G
Vnext=L*(N-k-1)/(m-1)**2*y**2-y*(L*z+t)/(m-1)-L*U*z**2/(2*(m-1)**2)+an*F1+bn*G1
results={}
def check(name, expr):
    if name in ('generic_step','matrix_product_ratio','a_difference','b_difference'):
        expr=expr.subs(N,(s.Symbol('m')+k)/2)
    variables=(d,p,z,q,t,F,G,F1,G1)
    zero=dict.fromkeys(variables,s.S.Zero)
    raw=[expr.subs(zero)]
    for i,x in enumerate(variables):
        raw.append(s.diff(expr,x).subs(zero))
        for y in variables[i:]:
            raw.append(s.diff(expr,x,y).subs(zero))
    residuals=[s.factor(s.together(v)) for v in raw]
    bad=[str(v) for v in residuals if v!=0]
    results[name]={'coefficient_count':len(residuals),'nonzero_coefficients':bad,'passed':not bad}
    print(name, results[name], flush=True)
    assert not bad
check('generic_step',Vnext-V-((an-a)*If1+a*If01+(bn-b)*Ig1+b*Ig01-Q))
check('initial_N_ge_2',(-L*d**2/(4*N)+Vnext-(a*If0-L*p**2/(4*N)+(an-a)*If1+a*If01+bn*Ig1-Q)).subs(k,0))
Qend=L/2*((z+q-(d-p)/(N+1))**2+(q+N*p/(N+1)-d/(N+1))**2)
Vendprev=L*d**2/(N+1)**2-d*(L*p+t)/(N+1)-L*(N-1)*p**2/(2*(N+1)**2)+N*F/(N+1)+(N-1)*G/(N+1)
check('terminal_N_ge_2',F1+G1-Vendprev-(If1/(N+1)+N*If01/(N+1)+2*Ig1/(N+1)+(N-1)*Ig01/(N+1)-Qend))
check('N_eq_1',F1+G1-L*d**2/4-(If0/2-L*p**2/4+If1/2+If01/2+Ig1-Qend.subs(N,1)))
M=s.Matrix([[k*(k+1)*m*(m-1), k*(k+1)*(m-1)**2*(k+m+1)],[(2*k+1)*m-k,(m-1)*(k*(k+3)*m+m+1)]])
ratio=(M*s.Matrix([U,1]))
check('matrix_product_ratio',ratio[0]/ratio[1]-T)
check('a_difference',an-a-(2*N+1)/(m*(m-1)))
check('b_difference',bn-b-2*N/(m*(m-1)))
(ROOT/'exact_audit.json').write_text(json.dumps(results,indent=2))
