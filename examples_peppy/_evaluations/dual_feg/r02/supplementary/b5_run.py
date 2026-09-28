import importlib.util
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',root/'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import numpy as np
import sympy as sp
import pepflow as pf
import dual_feg_setup as setup
notebook_dir=root
REPO_ROOT=runtime.REPO_ROOT
certificate=json.loads((root/'state/dual_feg_b4.json').read_text())
N_int=certificate['N_verify']
N=sp.Integer(N_int)
params_sp: dict[str,pf.NUMERICAL_TYPE]={'L':sp.Integer(1),'R':sp.Integer(1)}
ctx,pb,obj=setup.get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
for field in ('certificate_check_code','decomposition_code','grouping_code','basis_code'):
    exec(certificate[field])
coeff_by_k={int(k):np.array(C,dtype=float).reshape((len(V_k_basis(int(k))),len(V_k_basis(int(k))))) for k,C in certificate['coeff_by_k'].items()}
required_indices=list(range(N_int+1))
exec((root/'supplementary/b4_structure.py').read_text(encoding='utf-8-sig'))
for filename in ('b5_definitions.py','b5_step.py','b5_base.py','b5_terminal.py','b5_boundary.py','b5_small_domain.py'):
    print('Executing',filename,flush=True)
    exec(compile((root/'supplementary'/filename).read_text(encoding='utf-8-sig'),filename,'exec'))
(root/'supplementary/b5-exact-checks.json').write_text(json.dumps({'proof_checks':proof_checks,'exact_residuals':exact_residuals,'local_multipliers':{str(k):str(v) for k,v in local_solution[0].items()}},indent=2),encoding='utf-8')
