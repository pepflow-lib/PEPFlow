from pathlib import Path
import nbformat
root=Path.cwd()
for name in ('step','derive'):
    p=root/f'supplementary/b5_{name}.py'
    source=p.read_text(encoding='utf-8-sig')
    source=source.replace('; PB=', '\nPB=').replace('; PBn=', '\nPBn=').replace('; PT=', '\nPT=')
    if name=='step':
        source='from typing import Any\n'+source
        source=source.replace('params_symbolic=', 'params_symbolic: dict[str, Any]=')
    else:
        source=source.replace('unknown_params=', 'unknown_params: dict[str, Any]=')
    p.write_text(source,encoding='utf-8')
p=root/'feg_example_lyap.ipynb'
nb=nbformat.read(p,as_version=4)
for cell in nb.cells:
    if cell.cell_type!='code':continue
    source=cell.source.replace('; PB=', '\nPB=').replace('; PBn=', '\nPBn=').replace('; PT=', '\nPT=')
    if source.startswith('k_sp,N_sp='):
        source='from typing import Any\n'+source
        source=source.replace('params_symbolic=', 'params_symbolic: dict[str, Any]=')
    if source.startswith('a_now,b_now,'):
        source=source.replace('unknown_params=', 'unknown_params: dict[str, Any]=')
    cell.source=source
nbformat.write(nb,p)
