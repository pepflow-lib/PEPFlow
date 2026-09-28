import os,sys,json,hashlib,contextlib
from pathlib import Path
root=Path.cwd().resolve()
original=root.parents[3]/'dual_feg/r02'
for key in ['TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME']:
    p=root/'runtime'/key.lower();p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
notebook=json.loads((original/'dual_feg_example_lyap.ipynb').read_text(encoding='utf-8'))
repo=original/'supplementary/approved'
sys.path.insert(0,str(repo))
g={'notebook_dir':original,'repo_root':repo,'Path':Path,'sys':sys}
completed=[]
with (root/'replay.log').open('w',encoding='utf-8') as out,contextlib.redirect_stdout(out):
    for cell in notebook['cells']:
        if cell['cell_type']!='code' or cell['id']=='20e3a46a':continue
        source=''.join(cell['source'])
        # Skip runtime import (would create directories in frozen submission) and all plotting/display.
        source='\n'.join(line for line in source.splitlines() if not line.startswith(('import runtime','import matplotlib.pyplot','assert runtime.','plt.','pf.pprint_labeled_matrix(')))
        print('CELL',cell['id'],flush=True)
        exec(compile(source,'notebook#'+cell['id'],'exec'),g)
        completed.append(cell['id'])
    result={'completed_cells':completed,'numeric_residuals':g['residuals'],'rank_N6':g['ranks'],'coverage_N6':g['coverage_residuals'],'quadratic_reconstruction':g['coefficient_residuals'],'full_reconstruction':g['component_residuals'],'exact_residuals':g['exact_residuals'],'proof_checks':g['proof_checks']}
    # Recheck N=4 from its own frozen certificate using identical submitted validation and grouping cells.
    g['certificate']=json.loads((original/'supplementary/b2-N4-certificate.json').read_text())
    g['N_int']=4;g['N']=g['sp'].Integer(4)
    ctx,pb,obj=g['get_pep_setup'](4,g['params_sp']);pb.set_relaxed_constraints(g['certificate']['relaxed_constraints']);ctx.set_as_current()
    g.update(ctx=ctx,pb=pb,obj=obj)
    for cid in ['4b314d75','6bd18830','beb981ea']:
        source=''.join(next(c for c in notebook['cells'] if c['id']==cid)['source']);exec(compile(source,'notebook#'+cid,'exec'),g)
    result.update(rank_N4=g['ranks'],coverage_N4=g['coverage_residuals'])
(root/'replay-results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('Replay complete',len(completed),'code cells; N=4 and N=6 checked')
