import json
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=['b5_definitions.py','b5_step.py','b5_base.py','b5_terminal.py','b5_boundary.py','b5_small_domain.py']
markers=['b4=json.loads','t_s,n_s=','ctx_base=','ctx_terminal=','ctx_bound=','ctx_one=']
nbpath=root/'dual_feg_example_lyap.ipynb'
nb=json.loads(nbpath.read_text(encoding='utf-8'))
for filename,marker in zip(files,markers):
    p=root/'supplementary'/filename
    source=p.read_text(encoding='utf-8-sig')
    if filename=='b5_definitions.py':
        source='from typing import cast\n'+source
    else:
        source=re.sub(r'resolve_parameters=(\{[^\n]+\})\)',r'resolve_parameters=cast(dict[str,pf.NUMERICAL_TYPE],\1))',source)
    p.write_text(source,encoding='utf-8')
    for c in nb['cells']:
        old=''.join(c['source'])
        if c['cell_type']=='code' and old.startswith(marker):
            c['source']=source.splitlines(keepends=True)
            break
    else:
        raise RuntimeError(marker)
nbpath.write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf-8')
