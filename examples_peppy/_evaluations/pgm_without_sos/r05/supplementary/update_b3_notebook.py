import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from owned_runtime import configure, ROOT
configure()
import os
import hashlib
import nbformat
from nbclient import NotebookClient

os.environ['JUPYTER_PATH']=str(ROOT/'supplementary/.runtime/jupyter')
path=ROOT/'pgm_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
for c in nb.cells:
    if c.cell_type=='code' and "for filename in ('pgm_relaxed.json','pgm_b2.json'):" in c.source and "if not (notebook_dir/'state'/filename).exists():" not in c.source:
        c.source=c.source.replace("    (notebook_dir/'state'/filename).write_text(json.dumps(state_b2,indent=2,allow_nan=False))", "    if not (notebook_dir/'state'/filename).exists():\n        (notebook_dir/'state'/filename).write_text(json.dumps(state_b2,indent=2,allow_nan=False))")
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Partial-sum'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Identify the vectors'))
new=[nbformat.v4.new_markdown_cell(r'''## Partial-sum Lyapunov construction and rank profile

For the selected numerical certificate, let $I_c\le0$ denote each interpolation residual and let $Q_j\succeq0$ be the retained reverse-LDL quadratic pieces. We form
$$V_0=0,\qquad V_{k+1}-V_k=\sum_{c\in A_k}\lambda_c I_c-\sum_{j\in B_k}Q_j.$$
Star-to-$x_j$ and consecutive pairs ending at $x_j$ enter step $j-1$; the initial star-to-$x_0$ residual enters the first increment. The code below assigns each LDL piece by its actual pivot in the chronological basis, preserving every factor. Thus the sequence has the nonincreasing sign convention. All interpolation terms and all Gram pieces are included; the initial-distance constraint is retained for the boundary argument.

Both $N=4$ and $N=6$ give interior rank $5$, with only $V_0,V_N$ excluded and absolute rank tolerance $10^{-4}$ on unscaled Gram coordinates. This is numerical structural evidence. The final partial sum has rank $1$, and full scalar-coordinate coverage is checked below.'''),
nbformat.v4.new_code_cell("certificate=json.loads((notebook_dir/'state/pgm_b2.json').read_text())\nREPO_ROOT=notebook_dir  # Source-hash paths in this certificate are attempt-relative.\nassert Path(pf.__file__).resolve()==repo_root/'pepflow/__init__.py'\nN_int=certificate['N_verify']\nparams_sp: dict[str,pf.NUMERICAL_TYPE]={'L':sp.Integer(1),'R':sp.Integer(1)}\nctx,pb,obj=get_pep_setup(N_int,params_sp)\npb.set_relaxed_constraints(certificate['relaxed_constraints'])\nctx.set_as_current()")]
for filename in ('b3_certificate_check.py','b3_decomposition.py','b3_grouping.py','b3_save.py'):
    new.append(nbformat.v4.new_code_cell((ROOT/'supplementary'/filename).read_text(encoding='utf-8-sig')))
nb.cells[start:end]=new
nbformat.write(nb,path)
NotebookClient(nb,timeout=180,kernel_name='pgm-owned',resources={'metadata':{'path':str(ROOT)}}).execute()
nbformat.write(nb,path)
for i,c in enumerate(nb.cells):
    if c.cell_type=='markdown':
        assert not any(x in c.source for x in ('\x0c','\x0b','\r',r'\(',r'\['))
    if i>=start:
        for output in c.get('outputs',[]):
            if output.output_type=='stream': print('CELL',i,output.text)
checklist=ROOT/'supplementary/pgm_example_lyap_checklist.md'
lines=checklist.read_text(encoding='utf-8').splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'): lines[i]='Last reviewed block: B3'
    if line.startswith('SHA-256:'): lines[i]='SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()
    if line.startswith('| 9 |'): lines[i]=f'| 9 | partial-sum Lyapunov construction and rank profile | verified | {start}–{start+5} | Saved certificate revalidated; both horizons recomputed, rank 5 confirmed; visible construction, full-coordinate coverage and sign checks pass. |'
    if line.startswith('| 10 |'): lines[i]=f'| 10 | special-vector identification | pending | {start+6} | Block 4 obligation. |'
    if line.startswith('| 11 |'): lines[i]=f'| 11 | coefficient extraction and closed-form V_k | pending | {start+7} | Blocks 4–5 obligation. |'
    if line.startswith('| 12 |'): lines[i]=f'| 12 | symbolic step, base, and boundary identities | pending | {start+8} | Block 5 obligation. |'
checklist.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Fresh kernel and Markdown checks passed.')
