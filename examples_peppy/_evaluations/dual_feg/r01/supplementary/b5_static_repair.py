import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
replacements={"pm_step=pf.ExpressionManager(ctx_der,resolve_parameters={'t_exact':Ts,'N_exact':Ns,'L_exact':Ls})":"step_mapping: dict[str, Any]={'t_exact':Ts,'N_exact':Ns,'L_exact':Ls}\npm_step=pf.ExpressionManager(ctx_der,resolve_parameters=step_mapping)","pm_one=pf.ExpressionManager(ctx_one,resolve_parameters={'L_exact':Ls})":"one_mapping: dict[str, Any]={'L_exact':Ls}\npm_one=pf.ExpressionManager(ctx_one,resolve_parameters=one_mapping)"}
for name in ['b5_step.py','b5_last.py']:
    p=root/'supplementary'/name
    s=p.read_text(encoding='utf-8-sig')
    for old,new in replacements.items(): s=s.replace(old,new)
    p.write_text(s,encoding='utf-8')
p=root/'dual_feg_example_lyap.ipynb'
nb=json.loads(p.read_text())
for c in nb['cells']:
    if c['cell_type']=='code':
        s=''.join(c['source'])
        for old,new in replacements.items(): s=s.replace(old,new)
        c['source']=s
p.write_text(json.dumps(nb,indent=1))
