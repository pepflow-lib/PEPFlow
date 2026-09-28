import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from owned_runtime import configure, ROOT
configure()
import os
import json
import hashlib
import nbformat
from nbclient import NotebookClient

os.environ['JUPYTER_PATH']=str(ROOT/'supplementary/.runtime/jupyter')
path=ROOT/'pgm_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Dense and relaxed'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Partial-sum'))
sections=(ROOT/'supplementary/b2_cells.py').read_text(encoding='utf-8-sig').split('# CELL\n')[1:]
new=[nbformat.v4.new_markdown_cell('## Dense and relaxed proof solves\n\nKeep consecutive forward interpolation pairs and all pairs from $x_\\star$ in both function classes. The dense solve is cached from this attempt; the selected relaxed solve below captures every multiplier and the same Gram remainder.')]
new.extend(nbformat.v4.new_code_cell(s.strip()) for s in sections[:2])
new.append(nbformat.v4.new_markdown_cell(r'''## Lambda and S verification

The numerical fractions suggest forward weights $a_k=(k+1)/(2N-k)$ for $f$ and $b_k=k/(2N-k)$ for $g$. Weights from $x_\star$ are successive differences, taking the terminal cumulative weight to be $1$. These formulas are candidates. Their all-horizon validity and the positivity of the resulting Gram remainder remain unproved.

For residuals $R_c\le0$, the complete numerical identity is
$$h(x_N)-h(x_\star)-\tau R^2-\sum_c\lambda_cR_c+S=0.$$
The sum includes the initial residual. Nonnegative multipliers and $S\succeq0$ establish the sampled upper bound. All scalar, Gram and constant coordinates are checked below. No supplied SOS aid was consulted.'''))
new.extend(nbformat.v4.new_code_cell(s.strip()) for s in sections[2:])
nb.cells[start:end]=new
nbformat.write(nb,path)
NotebookClient(nb,timeout=180,kernel_name='pgm-owned',resources={'metadata':{'path':str(ROOT)}}).execute()
nbformat.write(nb,path)
for c in nb.cells:
    if c.cell_type=='markdown':
        assert not any(x in c.source for x in ('\x0c','\x0b','\r',r'\(',r'\['))
for i,c in enumerate(nb.cells):
    if start<=i<start+len(new):
        for output in c.get('outputs',[]):
            if output.output_type=='stream':
                print('CELL',i,output.text)
checklist=ROOT/'supplementary/pgm_example_lyap_checklist.md'
text=checklist.read_text(encoding='utf-8')
lines=text.splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'): lines[i]='Last reviewed block: B2'
    if line.startswith('SHA-256:'): lines[i]='SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()
    if line.startswith('| 7 |'): lines[i]='| 7 | dense and relaxed proof solves | verified | 8–10 | Both groups summarized; relaxation preserves dense optimum; complete live capture. |'
    if line.startswith('| 8 |'): lines[i]='| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 11–14 | Both-group candidates, reverse LDL, all-coordinate identity, cone checks and executed residuals; analytic statuses explicit. |'
    if line.startswith('| 9 |'): lines[i]='| 9 | partial-sum Lyapunov construction and rank profile | pending | 15 | Block 3 obligation. |'
    if line.startswith('| 10 |'): lines[i]='| 10 | special-vector identification | pending | 16 | Block 4 obligation. |'
    if line.startswith('| 11 |'): lines[i]='| 11 | coefficient extraction and closed-form V_k | pending | 17 | Blocks 4–5 obligation. |'
    if line.startswith('| 12 |'): lines[i]='| 12 | symbolic step, base, and boundary identities | pending | 18 | Block 5 obligation. |'
checklist.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'fresh_kernel':'passed','markdown_checks':'passed','notebook':str(path)}))
