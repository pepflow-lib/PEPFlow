import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import contextlib
import json
import numpy as np
from pgm_setup import get_pep_setup
notebook_dir=runtime.ROOT
with (notebook_dir/'supplementary/b3-certificate-recheck.log').open('w') as log,contextlib.redirect_stdout(log):
    exec(compile((notebook_dir/'supplementary/b2_notebook_cells.py').read_text(encoding='utf-8-sig'),'b2_check','exec'))
b2=json.loads((notebook_dir/'state/pgm_b2.json').read_text())
keys=('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')
assert hashlib.sha256(json.dumps({k:b2[k] for k in keys},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()==b2['certificate_id']
assert b2['named_dual_values']==selected['named_dual_values'] and b2['S_matrix']==selected['S_matrix']
coords={}
assign={}
for c, *_ in entries:
    if c.name=='initial_condition' or duals[c.name] is None:
        continue
    residual=c.lhs-c.rhs
    value=pm.eval_scalar(duals[c.name]*(pf.Scalar.zero()+residual))
    coords[c.name]=np.asarray(value.inner_prod_coords,dtype=float)
    first,second=c.name.split(':')[1].split(',')
    assign[c.name]=int(second[2:])-1
pieces=[D[i,i]*np.outer(E[i],E[i]) for i in range(len(D))]
assert np.allclose(sum(pieces),S_array,atol=1e-5,rtol=0)
labels=selected['basis_vectors']
times=[]
for label in labels:
    if label in ['x_0','x_star','grad_f(x_star)']:
        times.append(0)
    else:
        times.append(int(label.split('x_')[1].split(')')[0]))
trials=[]
for rule in ['latest','earliest_pivot','all_end','none_until_end']:
    sas=[]
    for i,row in enumerate(E):
        if rule=='latest':
            t=max([times[j] for j,v in enumerate(row) if abs(v)>1e-5],default=0)
        elif rule=='earliest_pivot':
            t=times[len(labels)-1-i]
        else:
            t=N
        sas.append(max(0,t-1))
    ranks=[0]; singular=[[]]; matrices=[np.zeros_like(S_array)]
    partial=sum((v for name,v in coords.items() if assign[name]==-1),np.zeros_like(S_array))
    for k in range(N):
        partial=partial+sum((v for name,v in coords.items() if assign[name]==k),np.zeros_like(S_array))
        partial=partial-sum((p for i,p in enumerate(pieces) if sas[i]==k),np.zeros_like(S_array))
        sv=np.linalg.svd(partial,compute_uv=False)
        ranks.append(int(np.sum(sv>1e-4)));singular.append(sv.tolist());matrices.append(partial.tolist())
    row={'rule':rule,'rank_profile':ranks,'singular_values':singular,'S_assignment':sas}
    trials.append(row)
    print(rule,ranks)
(notebook_dir/'supplementary/b3-rank-trials-n4.json').write_text(json.dumps(trials,indent=2))
