import importlib.util
import json
import hashlib
import inspect
from pathlib import Path
import numpy as np
import sympy as sp
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',root/'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import pepflow as pf
import dual_feg_setup as setup
from certificate import capture
notebook_dir=root
get_pep_setup=setup.get_pep_setup
n=4
ctx,pb,obj=get_pep_setup(n,{'L':1,'R':1})
dense4=capture(ctx,pb,obj,{'L':1,'R':1})
dense4['N']=n
(root/'supplementary/b2-N4-dense.json').write_text(json.dumps(dense4,indent=2))
ctx,pb,obj=get_pep_setup(n,{'L':1,'R':1})
keep={'initial_condition',f'A monotone:x_{n},x_star',f'A Lipschitz:x_{n-1},x_{n}'}
keep.update(f'A monotone:x_{n},y_{k}' for k in range(n-1))
keep.update(f'A Lipschitz:x_{k},y_{k}' for k in range(n-1))
pb.set_relaxed_constraints([name for name in dense4['named_dual_values'] if name not in keep])
selected4=capture(ctx,pb,obj,{'L':1,'R':1})
selected4['N']=n
selected4['sparsity_selection']={'method':'terminal monotonicity to star and y_0..y_(N-2); Lipschitz x_k,y_k for k<N-1 and x_(N-1),x_N','dense_gap':abs(selected4['opt_value']-dense4['opt_value'])}
(root/'supplementary/b2-N4-relaxed.json').write_text(json.dumps(selected4,indent=2))
source=(root/'supplementary/b2_verify.py').read_text(encoding='utf-8-sig')
source=source.split('# BEGIN NOTEBOOK VERIFICATION',1)[1]
source=source.replace("state/dual_feg_relaxed.json","supplementary/b2-N4-relaxed.json").replace("state/dual_feg_dense.json","supplementary/b2-N4-dense.json")
source=source.replace("__import__('inspect').getsource(lambda_candidate)","inspect.getsource(setup) if False else formula_source")
source=source.replace("for filename in ('dual_feg_b2.json','dual_feg_relaxed.json'):","for filename in ('b2-N4-certificate.json',):").replace("root/'state'/filename","root/'supplementary'/filename")
formula_source=source.split('def lambda_candidate',1)[1].split('\nlambda_error',1)[0]
formula_source='def lambda_candidate'+formula_source
(root/'supplementary/b2-N4-verification-source.py').write_text(source)
exec(compile(source,str(root/'supplementary/b2-N4-verification-source.py'),'exec'))
print('Additional N=4 coherent certificate saved; main N=6 certificate unchanged.')
