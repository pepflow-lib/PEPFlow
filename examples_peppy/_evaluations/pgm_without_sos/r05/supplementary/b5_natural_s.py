import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from owned_runtime import configure,ROOT
configure()
import json
import sympy as sp
import pepflow as pf
from pgm_setup import get_pep_setup,f,g
b4=json.loads((ROOT/'state/pgm_b4.json').read_text())
exec(b4['lamb_code'],globals())
N=4
ctx,pb,_=get_pep_setup(N,{})
pm=pf.ExpressionManager(ctx,resolve_parameters={'L':sp.S.One,'R':sp.S.One})
S=sp.Rational(1,4*N)*(ctx['x_0']-ctx['x_star'])**2-pb.performance_metric
for owner in ctx.func_to_triplets:
    for c in owner.get_interpolation_constraints(ctx):
        a,b=c.name.split(':')[1].split(',')
        S+=lamb(str(owner),a,b,N)*(c.lhs-c.rhs)
M=sp.Matrix(pm.eval_scalar(S,sympy_mode=True).inner_prod_coords)
vectors=[ctx['x_0']-ctx['x_star']]+[ctx[f'x_{i}']-ctx[f'x_{i+1}'] for i in range(N)]+[f.grad(ctx[f'x_{i}'])-f.grad(ctx['x_star']) for i in range(N+1)]
B=sp.Matrix.hstack(*[sp.Matrix(pm.eval_vector(v,sympy_mode=True).coords) for v in vectors])
inv=(B.T*B).inv()*B.T
C=(inv*M*inv.T).applyfunc(sp.cancel)
assert B*C*B.T==M
print('basis d0,t0..t3,p0..p4')
print(C)
P=C[N+1:,N+1:]
print('P',P,'leading minors',[sp.factor(P[:i,:i].det()) for i in range(1,N+2)])
print('cross',C[:N+1,N+1:])
print('reduced',(C[:N+1,:N+1]-C[:N+1,N+1:]*P.inv()*C[N+1:,:N+1]).applyfunc(sp.factor))
