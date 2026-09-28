import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from b2_explore import acquire
import runtime

paths = [runtime.ROOT/'pgm_setup.py',runtime.ROOT/'supplementary/helpers/runtime.py']
allowlist=json.loads((runtime.APPROVED/'allowlist.json').read_text())
paths += [Path(p) for p in allowlist['exact_read_files'] if '\\pepflow\\' in p and p.endswith('.py')]
hashes={str(p.relative_to(runtime.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
drop=json.loads((runtime.ROOT/'supplementary/b2-consecutive.json').read_text())['relaxed_constraints']
ctx,pb,result,data=acquire(4,drop)
data['source_hashes']=hashes
data['constraint_metadata']={}
data['named_dual_values']={}
entries=[(c,'initial',None,None) for c in pb.init_conditions]
for owner in ctx.func_to_triplets:
    groups=ctx.get_constraint_data(owner)
    entries.extend((c,'interpolation',str(owner),str(group)) for group,cs in groups.sc_dict.items() for c in cs)
    assert not groups.psd_dict
for c,origin,owner,group in entries:
    relaxed=c.name in drop
    value=result.get_dual_value(c.name)
    assert value is not None or relaxed
    data['named_dual_values'][c.name]=None if relaxed else float(value)
    data['constraint_metadata'][c.name]=dict(origin=origin,owner=owner,group=group,kind='scalar',comparator=c.cmp.value,shape=[],relaxed=relaxed)
data['basis_scalars']=[str(v) for v in ctx.basis_scalars()]
for p in paths:
    assert hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p.relative_to(runtime.ROOT))]
(runtime.ROOT/'state/pgm_selected_raw.json').write_text(json.dumps(data,indent=2))
print('selected coherent capture',data['status'],data['opt_value'])
