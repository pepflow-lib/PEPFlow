import sympy as sp
k,t,c,b=sp.symbols('k t c b')
a=c+(k+2)/(2*(t-1));d=((2*k+1)*t-k)/(2*(t-1)**2);e=(k+1)/(2*(t-1));v=(k+1)/(2*t*(t-1));w=(k*t+1)/(2*(t-1)**2)
m=(k*t*t-k*t+k+1)/(2*t*(t-1)**2)
delta=sp.factor(d-e*e/a)
rec=k*(k+1)*(t-1)*(2*c*t*(t-1)+k+t+1)/(2*t*t*(2*c*(t-1)*((2*k+1)*t-k)+(k*k+3*k+1)*t+1))
print('checking coefficient',flush=True)
print(sp.factor(m-rec-v*v/a-(w-e*v/a)**2/delta),flush=True)
A,D,E,V,W=sp.symbols('A D E V W',nonzero=True)
p,z,r=sp.symbols('p z r')
rho=V*V/A+(W-E*V/A)**2/(D-E*E/A)
Q=rho*p*p+D*z*z+A*r*r+2*W*p*z+2*V*p*r+2*E*z*r
squares=A*(r+E/A*z+V/A*p)**2+(D-E*E/A)*(z+(W-E*V/A)/(D-E*E/A)*p)**2
print('generic square identity',sp.factor(Q-squares),flush=True)
