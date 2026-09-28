import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
import sympy as sp
import pepflow as pf
import pgm_setup as mod

n=4
ctx,pb,_=mod.get_pep_setup(n,{'L':1,'R':1})
pm=pf.ExpressionManager(ctx,resolve_parameters={'L':1,'R':1})
data=json.loads((runtime.ROOT/'supplementary/b2-consecutive.json').read_text())
N=sp.Integer(n)
xstar=ctx['x_star']
a_star=mod.f.grad(xstar)
S=pf.Scalar.zero()
for i in range(1,n+1):
    xprev=ctx[f'x_{i-1}']; x=ctx[f'x_{i}']
    ap=mod.f.grad(xprev); a=mod.f.grad(x); s=mod.g.grad(x)
    c1=N/((2*N+1-i)*(2*N-i))
    u1=i/(2*N)*a+(2*N-i)/(2*N)*ap-a_star
    c2=((i-1)/(2*N-i)*(2*N+2)/(2*N+1)+2*N/((2*N-i)**2*(2*N+1)))/2
    u2=ap+s-(xprev-xstar)/(2*N+1-i)
    c3=i/(2*N+1-i)*(2*N)/(2*N+1)/2
    u3=(2*N+1)/(2*N)*(a+s)-(ap+s)/(2*N)-(x-xstar)/(2*N-i)
    S += c1*u1**2+c2*u2**2+c3*u3**2
A=np.asarray(pm.eval_scalar(S).inner_prod_coords,dtype=float)
B=np.asarray(data['S_matrix'])
print('SOS scale least squares',np.sum(A*B)/np.sum(A*A))
print('SOS raw difference',np.max(np.abs(A-B)))
weighted=pf.Scalar.zero()
for owner in (mod.f,mod.g):
    for c in owner.get_interpolation_constraints(ctx):
        if c.name in data['named_dual_values']:
            pair=c.name.split(':')[1].split(',')
            left,right=pair
            j=int(right[2:])
            if owner is mod.f:
                alpha=lambda t:sp.Rational(t,2*n+1-t)
                val=alpha(j) if left!='x_star' else (alpha(j+1)-alpha(j) if j<n else 1-alpha(n))
            else:
                beta=lambda t:sp.Rational(t,2*n-t)
                val=beta(j-1) if left!='x_star' else beta(j)-beta(j-1)
            weighted+=val*(c.lhs-c.rhs)
            print(c.name,'candidate',val,'error',float(val)-data['named_dual_values'][c.name])
weighted+=sp.Rational(1,4*n)*(pb.init_conditions[0].lhs-pb.init_conditions[0].rhs)
diff=pm.eval_scalar(pb.performance_metric-sp.Rational(1,4*n)-weighted+S)
print('exact identity',max(abs(v) for v in diff.inner_prod_coords.flat),max(abs(v) for v in diff.func_coords),diff.offset)
