from pathlib import Path
import os,sys,json,contextlib,traceback,re
v=Path(chr(92)*2+'?'+chr(92)+str(Path(__file__).resolve().parent))
os.chdir(v)
for key in ['TEMP','TMP','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','JUPYTER_DATA_DIR','XDG_CACHE_HOME']:
 p=v/'posthoc_runtime'/key;p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
os.environ['MPLBACKEND']='Agg'
nb=json.loads((v/'feg_example_lyap.ipynb').read_text(encoding='utf-8'))
adjust=[];results=[];ns={'__name__':'__main__'}
with (v/'replay-output.txt').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
 try:
  for c in nb['cells']:
   if c['cell_type']!='code':continue
   cid=c['id'];before=''.join(c['source']);src=before
   if cid in ['69608ddc','9817db5b','dd70138b']:
    adjust.append(dict(cell=cid,before=before,after='',reason='Discovery/search cell inspected but omitted from validation; explicit submitted formulas and saved coefficients are verified elsewhere.'))
    results.append(dict(cell=cid,status='INSPECTED_NOT_REPLAYED'));continue
   src=src.replace('notebook_dir = Path.cwd().resolve()',"notebook_dir = Path("+repr(str(v))+')')
   src=src.replace('plt.show()','plt.close(fig)')
   src=src.replace('C=find_symmetric_coefficient_matrix(lyap[k],chosen,pep_context=ctx,resolve_parameters=params_sp,**extraction_tolerances)',"C=np.asarray(json.loads((notebook_dir/'state/feg_b4.json').read_text())['coeff_by_k'][str(k)],dtype=float)")
   lines=[]
   for line in src.splitlines():
    if line.lstrip().startswith('pf.pprint_labeled_matrix('):
     line=line[:len(line)-len(line.lstrip())]+"print('Matrix display omitted; mathematical checks retained')"
    lines.append(line)
   src='\n'.join(lines)
   if src!=before:adjust.append(dict(cell=cid,before=before,after=src,reason='Execution-only path/display changes; saved B4 coefficients loaded rather than rediscovered. All identities and assertions retained.'))
   assert not re.search(r'[A-Z]:[/\\]',src) or cid=='9a11736a',cid
   print('REPLAY CELL',cid,flush=True)
   exec(compile(src,'notebook#'+cid,'exec'),ns)
   results.append(dict(cell=cid,status='PASS'))
  print('ALL SELECTED CELLS PASSED')
 except BaseException as e:
  traceback.print_exc();results.append(dict(cell=cid,status='ERROR',error=repr(e)))
(v/'execution-adjustments.json').write_text(json.dumps(adjust,indent=2),encoding='utf-8')
summary=dict(cells=results,python=sys.executable,environment={k:os.environ[k] for k in ['TEMP','TMP','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','JUPYTER_DATA_DIR','XDG_CACHE_HOME']})
for k in ['residuals','coefficient_residuals','component_residuals','independence','ranks','step_verified','base_verified','boundary_verified','signs_verified','domain_verified','normalization_verified','formula_residuals']:
 if k in ns:summary[k]=ns[k]
(v/'replay-results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
