import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import hashlib
import numpy as np
import pepflow as pf
from bppm_setup import get_pep_setup
from certificate import solve_capture
notebook_dir=runtime.ROOT
folder=notebook_dir/'supplementary/N6'
folder.mkdir(exist_ok=True)
source=(folder/'verification-symbolic.py').read_text(encoding='utf-8-sig')
exec(compile(source,'N6/verification.py','exec'))
saver=(notebook_dir/'supplementary/save_b2.py').read_text(encoding='utf-8-sig')
saver=saver[saver.index('state={**b1,**certificate}'):saver.index("for filename in ('bppm_b2.json'")]
exec(compile(saver,'N6/state_capture','exec'))
state['notebook_selected_horizon']=4
state['closed_form_search']['reused_from']='state/bppm_b2.json; candidate formulas rechecked at N=6'
(folder/'certificate.json').write_text(json.dumps(state,indent=2,allow_nan=False))
print('Additional complete certificate saved:',state['certificate_id'])
print('Numerical checks:',state['numerical_checks'])

