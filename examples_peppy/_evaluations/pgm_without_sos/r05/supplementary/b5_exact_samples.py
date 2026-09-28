import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from owned_runtime import configure, ROOT
configure()
import json
import sympy as sp
import pepflow as pf
from pgm_setup import get_pep_setup,f,g

b4=json.loads((ROOT/'state/pgm_b4.json').read_text())
exec(b4['lamb_code'],globals())
all_samples={}
for N in (4,6,8):
    ctx,pb,obj=get_pep_setup(N,{})
    pm=pf.ExpressionManager(ctx,resolve_parameters={'L':sp.S.One,'R':sp.S.One})
    constraints=[]
    for owner in ctx.func_to_triplets:
        constraints.extend(owner.get_interpolation_constraints(ctx))
    weights={c.name:lamb(c.name.split(':')[0],*c.name.split(':')[1].split(','),N) for c in constraints}
    terms={c.name:weights[c.name]*(c.lhs-c.rhs) for c in constraints if weights[c.name]!=0}
    S=sp.Rational(1,4*N)*(ctx['x_0']-ctx['x_star'])**2-pb.performance_metric+sum(terms.values(),pf.Scalar.zero())
    ev=pm.eval_scalar(S,sympy_mode=True)
    M=sp.Matrix(ev.inner_prod_coords)
    assert all(sp.simplify(v)==0 for v in ev.func_coords)
    reduced=M.copy()
    # Eliminate future basis vectors without changing the lower-index block.
    schurs={len(M)-1:reduced.copy()}
    for p in range(M.rows-1,2,-1):
        assert reduced[p,p]!=0
        reduced-=reduced[:,p]*reduced[p,:]/reduced[p,p]
        reduced=reduced.applyfunc(sp.cancel)
        schurs[p-1]=reduced.copy()
    samples={}
    for k in range(1,N):
        prefix=sum((term for name,term in terms.items() if int(name.split(',')[1][2:])<=k),pf.Scalar.zero())
        P=sp.Matrix(pm.eval_scalar(prefix,sympy_mode=True).inner_prod_coords)
        V=P-schurs[2*k+4]
        vectors=[ctx['x_0']-ctx['x_star'],f.grad(ctx[f'x_{k}']),ctx[f'x_{k+1}']-ctx['x_star'],g.grad(ctx[f'x_{k+1}']),f.grad(ctx['x_star'])]
        B=sp.Matrix.hstack(*[sp.Matrix(pm.eval_vector(v,sympy_mode=True).coords) for v in vectors])
        inv=(B.T*B).inv()*B.T
        C=(inv*V*inv.T).applyfunc(sp.cancel)
        assert B*C*B.T==V
        samples[k]=[[str(v) for v in row] for row in C.tolist()]
        print('N,k',N,k,'C',C.tolist(),flush=True)
    all_samples[N]=samples
(ROOT/'supplementary/b5-exact-coefficient-samples.json').write_text(json.dumps(all_samples,indent=2))
