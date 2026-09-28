import json
from pathlib import Path
root=Path.cwd()
replacements={"ctx=selected_sample['ctx']; ctx.set_as_current()":"ctx=selected_sample['ctx']\nctx.set_as_current()","pm=selected_sample['pm']; lyap=selected_sample['lyap']":"pm=selected_sample['pm']\nlyap=selected_sample['lyap']","params_sp=selected_sample['params_sp']; N_int=selected_sample['N_int']":"params_sp=selected_sample['params_sp']\nN_int=selected_sample['N_int']","unique.append((label,v)); coords.append(row)":"unique.append((label,v))\n    coords.append(row)","C=np.zeros((0,0)); matrix=np.zeros((len(ctx.basis_vectors()),0))":"C=np.zeros((0,0))\n        matrix=np.zeros((len(ctx.basis_vectors()),0))"}
for part in ('load','scan','coefficients'):
    p=root/f'supplementary/b4_{part}.py'
    s=p.read_text(encoding='utf-8-sig')
    for a,b in replacements.items():
        s=s.replace(a,b)
    p.write_text(s)
p=root/'pgm_example_lyap.ipynb'
book=json.loads(p.read_text())
for c in book['cells']:
    if c['cell_type']=='code':
        s=''.join(c['source'])
        for a,b in replacements.items():
            s=s.replace(a,b)
        c['source']=s.splitlines(keepends=True)
p.write_text(json.dumps(book,indent=1))
