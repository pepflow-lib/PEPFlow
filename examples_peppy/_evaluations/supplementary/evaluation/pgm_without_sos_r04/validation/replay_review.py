"""Replay inspected submitted cells, without solving, plotting or altering submission."""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parent
assert Path.cwd().resolve() == root
for key in ('TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME'):
    path = root / 'review_runtime' / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
os.environ['MPLBACKEND'] = 'Agg'
sys.path[:0] = [str(root/'supplementary/approved'), str(root), str(root/'supplementary/helpers')]
nb = json.loads((root/'pgm_example_lyap.ipynb').read_text(encoding='utf-8'))
env = {'__name__': '__main__'}
replayed = []
for index, cell in enumerate(nb['cells']):
    if cell['cell_type'] != 'code':
        continue
    source = ''.join(cell['source'])
    if index == 11:
        source = source[:source.index('fig, ax =')]
    print('REPLAY CELL', index, cell['id'], flush=True)
    exec(compile(source, 'submitted#'+cell['id'], 'exec'), env)
    replayed.append(cell['id'])
report = dict(replayed_cells=replayed, plotting_skipped=True, solver_runs=0,
              certificate_residuals=env['residuals'],
              reconstruction_residuals=env['component_residuals'],
              proof_checks=env['proof_checks'])
# Rebuild the submitted second-horizon certificate and grouping with the same source.
env['certificate'] = json.loads((root/'supplementary/sample_n6/certificate.json').read_text())
env['N_int'] = 6
env['ctx'],env['pb'],env['obj'] = env['saved_get_pep_setup'](6,env['params_sp'])
env['pb'].set_relaxed_constraints(env['certificate']['relaxed_constraints'])
exec(compile((root/'supplementary/b3_certificate_check.py').read_text(encoding='utf-8-sig'),'submitted_b3_certificate_check','exec'),env)
exec(compile((root/'supplementary/b3_grouping_cells.py').read_text(encoding='utf-8-sig'),'submitted_b3_grouping','exec'),env)
report['n6_rank_profile'] = env['ranks']
report['n6_coverage_residuals'] = env['coverage_residuals']
report['completed_utc'] = datetime.now(timezone.utc).isoformat()
(root/'replay_results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ALL REPLAY CHECKS PASSED', flush=True)
