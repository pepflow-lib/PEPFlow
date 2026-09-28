import importlib.util
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',root/'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
import sympy as sp
import pepflow as pf
from exact_lyapunov import local_context,phi,smooth_residual,convex_residual,step_square,assert_identity

K,Horizon,Lp=pf.Parameter('k'),pf.Parameter('N'),pf.Parameter('L')
k,N=sp.symbols('k N',integer=True,positive=True)
Ls=sp.Symbol('L',positive=True)
params={'k':k,'N':N,'L':Ls}
checks={}
ctx,F,G,H,star,x,xp=local_context('step',Lp)
LHS=phi(K+1,Horizon,Lp,xp,star,F,G)-phi(K,Horizon,Lp,x,star,F,G)
RHS=(2*Horizon+1)/((2*Horizon-K-1)*(2*Horizon-K))*smooth_residual(F,star,xp,Lp)
RHS+=2*Horizon/((2*Horizon-K-1)*(2*Horizon-K))*convex_residual(G,star,xp)
RHS+=(K+1)/(2*Horizon-K)*smooth_residual(F,x,xp,Lp)+K/(2*Horizon-K)*convex_residual(G,x,xp)
RHS-=step_square(K+1,Horizon,Lp,x,xp,star,F,G)
checks['step']=assert_identity('Interior 1<=k<=N-2',LHS,RHS,ctx,params)

ctx,F,G,H,star,x,xp=local_context('base',Lp)
LHS=phi(sp.S.One,Horizon,Lp,xp,star,F,G)-Lp/(4*Horizon)*(x-star)**2
RHS=smooth_residual(F,star,x,Lp)/(2*Horizon)
RHS+=(2*Horizon+1)/((2*Horizon-1)*(2*Horizon))*smooth_residual(F,star,xp,Lp)
RHS+=sp.S.One/(2*Horizon-1)*convex_residual(G,star,xp)
RHS+=smooth_residual(F,x,xp,Lp)/(2*Horizon)
RHS-=step_square(sp.S.One,Horizon,Lp,x,xp,star,F,G)
checks['base']=assert_identity('Base N>=2',LHS,RHS,ctx,params)

ctx,F,G,H,star,x,xp=local_context('boundary',Lp)
LHS=H(xp)-H(star)-phi(Horizon-1,Horizon,Lp,x,star,F,G)
RHS=smooth_residual(F,star,xp,Lp)/(Horizon+1)+2/(Horizon+1)*convex_residual(G,star,xp)
RHS+=Horizon/(Horizon+1)*smooth_residual(F,x,xp,Lp)+(Horizon-1)/(Horizon+1)*convex_residual(G,x,xp)
RHS-=step_square(Horizon,Horizon,Lp,x,xp,star,F,G)
checks['boundary']=assert_identity('Final step N>=2',LHS,RHS,ctx,params)

ctx,F,G,H,star,x,xp=local_context('one',Lp)
LHS=H(xp)-H(star)-Lp/4*(x-star)**2
RHS=sp.Rational(1,2)*smooth_residual(F,star,x,Lp)+sp.Rational(1,2)*smooth_residual(F,star,xp,Lp)
RHS+=convex_residual(G,star,xp)+sp.Rational(1,2)*smooth_residual(F,x,xp,Lp)
RHS-=step_square(sp.S.One,sp.S.One,Lp,x,xp,star,F,G)
checks['N1']=assert_identity('Exceptional N=1',LHS,RHS,ctx,params)
(root/'supplementary/b5-exact-checks.json').write_text(json.dumps(checks,indent=2))
