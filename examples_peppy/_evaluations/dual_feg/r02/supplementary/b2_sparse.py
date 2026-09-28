import importlib.util
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('runtime', root / 'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import dual_feg_setup as setup
from certificate import capture

dense = json.loads((root/'state/dual_feg_dense.json').read_text())
previous = root/'state/dual_feg_relaxed.json'
(root/'supplementary/b2-threshold-certificate.json').write_bytes(previous.read_bytes())
ctx,pb,obj = setup.get_pep_setup(6, {'L':1,'R':1})
keep = {'initial_condition','A monotone:x_6,x_star','A Lipschitz:x_5,x_6'}
keep.update(f'A monotone:x_6,y_{k}' for k in range(5))
keep.update(f'A Lipschitz:x_{k},y_{k}' for k in range(5))
dropped = [name for name in dense['named_dual_values'] if name not in keep]
pb.set_relaxed_constraints(dropped)
data = capture(ctx,pb,obj,{'L':1,'R':1})
data['N'] = 6
data['sparsity_selection'] = {'method':'terminal monotonicity to star and y_0..y_(N-2); Lipschitz x_k,y_k for k<N-1 and x_(N-1),x_N', 'dense_gap':abs(data['opt_value']-dense['opt_value'])}
previous.write_text(json.dumps(data,indent=2))
print('Objective and gap',data['opt_value'],data['sparsity_selection']['dense_gap'])
for name,val in data['named_dual_values'].items():
    if val is not None:
        print(name,val)
