import os, sys, json, hashlib, contextlib
from pathlib import Path
root = Path(__file__).resolve().parent
review = root.parent
settings = json.loads((review/'settings.json').read_text())
original = Path(settings['original_submission'])
for key in ['TEMP','TMP','TMPDIR','MPLCONFIGDIR','XDG_CACHE_HOME','JUPYTER_CONFIG_DIR','JUPYTER_RUNTIME_DIR','IPYTHONDIR']:
    dest = root/'runtime'/key
    dest.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(dest)
sys.path.insert(0,str(original/'supplementary'/'approved'))
nb=json.loads((original/'ogm_example_lyap.ipynb').read_text(encoding='utf-8'))
env={'notebook_dir':original,'Path':Path,'json':json,'sys':sys}
results={'hash_checks':{},'executed_cells':[]}
for name, expected in settings['submission_hashes'].items():
    actual=hashlib.sha256((original/name).read_bytes()).hexdigest()
    assert actual == expected, name
    results['hash_checks'][name]=True
with (root/'replay-output.txt').open('w',encoding='utf-8') as log, contextlib.redirect_stdout(log):
    for cell in nb['cells']:
        if cell['cell_type']!='code' or cell['id'] in ['66681432','a41ab4a7']:
            continue
        print('CELL',cell['id'],flush=True)
        exec(compile(''.join(cell['source']),cell['id'],'exec'),env)
        results['executed_cells'].append(cell['id'])
    results['symbolic']=env['symbolic_results']
    results['b2_N4']=env['revalidate'](env['certificate'])[-1]
    results['b2_N6']=env['revalidate'](env['certificate6'])[-1]
    results['b3']=[env['selected_observation'],env['other_observation']]
    results['b4_quadratic_residuals']=env['coefficient_residuals']
    results['b4_components']=env['component_residuals']
    results['formula_comparisons']=env['formula_comparisons']
results['all_replayed_checks_passed']=True
(root/'replay-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('All replayed checks passed;',len(results['executed_cells']),'cells.')
