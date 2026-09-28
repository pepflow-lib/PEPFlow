import sys, json, hashlib, os
from pathlib import Path
root=Path.cwd().resolve()
sys.path[:0]=[str(root/'supplementary/helpers'),str(root/'supplementary/approved'),str(root)]
import runtime
import numpy as np
import pepflow as pf
from ogm_setup import theta_sequence
report={}
for relative in ('state/ogm_b2.json','supplementary/ogm_b2_N6.json'):
    certificate=json.loads((root/relative).read_text())
    for name in ('b3_certificate_check.py','b3_decomposition.py','b3_grouping.py'):
        exec(compile((root/'supplementary'/name).read_text(encoding='utf-8-sig'),name,'exec'))
    report[str(N_int)]={'certificate_id':certificate['certificate_id'],'checks':fresh_checks,'rank_profile':ranks,'singular_values':singular_values,'coverage_residual':coverage_residual,'raw_identity_residual':coords_max(raw_diff)}
    if N_int==4:
        for name in ('b4_basis.py','b4_coefficients.py','b4_structure.py'):
            exec(compile((root/'supplementary'/name).read_text(encoding='utf-8-sig'),name,'exec'))
        report['b4']={'quadratic_errors':coefficient_residuals,'component_residuals':component_residuals}
for name in ('b5_symbolic_helpers.py','b5_step.py','b5_base.py','b5_terminal.py','b5_small_normalization.py'):
    exec(compile((root/'supplementary'/name).read_text(encoding='utf-8-sig'),name,'exec'))
report['symbolic']=symbolic_results
(root/'reviewer-replay.json').write_text(json.dumps(report,indent=2))
print('REVIEWER REPLAY COMPLETE')
