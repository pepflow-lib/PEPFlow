import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from runtime import configure
attempt,approved = configure()
import nbformat as nbf
from nbclient import NotebookClient
path=attempt/'ogm_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
nb.cells=nb.cells[:29]
md,code=nbf.v4.new_markdown_cell,nbf.v4.new_code_cell
sections=(attempt/'supplementary/b4_cells.py').read_text(encoding='utf-8-sig').split('# %%')[1:]
nb.cells.append(md('## Identify the vectors composing the Lyapunov function\nReplay the selected certificate and partial sums above. Search for interpretable vectors spanning their quadratic parts, while preserving every function and constant component.'))
first,second=sections[0].split('theta = theta_sequence(N_int)',1)
nb.cells.append(code(first))
nb.cells.append(md('### Candidate-vector scan\nCandidates include the initial displacement, tagged iterates, gradients, auxiliary iterates, shifted auxiliary vectors suggested by the terminal square, and pairwise differences. Remove duplicate coordinates and zero vectors before filtering.'))
nb.cells.append(code('theta = theta_sequence(N_int)'+second))
nb.cells.append(code(sections[1]))
nb.cells.append(md('### Selected basis pattern\nSearch every nonzero index, including the terminal exception, with the frozen independence, span, and sparsity tolerances.'))
nb.cells.append(code(sections[2]))
nb.cells.append(md(r'''The search selects the following sparse pattern. Put $d_0=x_0-x_\star$, and
$$q_k=z_k-x_\star-\frac{2\theta_k}{L}g_k\quad(1\leq k<N),\qquad q_N=z_N-x_\star-\frac{\theta_N}{L}g_N.$$
The ordered basis is $[d_0,q_k,g_k]$ in the interior, $[d_0,q_N]$ at the terminal index, and empty at $k=0$. The adopted basis agrees with the sparse-search result.
'''))
nb.cells.append(code(sections[3]))
nb.cells.append(md('### Coefficient matrices\nUse the ordered bases above. Display the symmetric quadratic matrices and every function-coordinate vector; off-diagonal entries count twice.'))
nb.cells.append(code(sections[4]))
nb.cells.append(code(sections[5]))
nb.cells.append(code(sections[6]))
nb.cells.append(md(r'''### Block 4 conclusion
All indices, including $0$ and $N$, reconstruct numerically. The candidate expression is $V_0=0$ and, for $1\leq k<N$,
$$V_k=\frac{2\theta_k^2}{\theta_N^2}(f(x_k)-f(x_\star))+
\frac{L}{2\theta_N^2}(\|q_k\|^2-\|d_0\|^2)-\frac{\theta_k^2}{L\theta_N^2}\|g_k\|^2,$$
with terminal expression
$$V_N=f(x_N)-f(x_\star)+\frac{L}{2\theta_N^2}(\|q_N\|^2-\|d_0\|^2).$$
There are no offset terms. These formulas agree with the numerical certificate at the selected horizon; Block 5 must establish the exact step, base, and terminal identities and their signs for arbitrary horizons, including $N=1$.
'''))
nb.cells.append(md('## Closed-form Lyapunov function and exact identities\nBlock 5 pending.'))
nb.cells.append(code((attempt/'supplementary/b4_save.py').read_text(encoding='utf-8-sig')))
os.environ['JUPYTER_PATH']=str(attempt/'supplementary/.runtime/jupyter')
NotebookClient(nb,timeout=120,kernel_name='ogm-own',resources={'metadata':{'path':str(attempt)}}).execute()
nb.cells.pop()
nbf.write(nb,path)
for i,c in enumerate(nb.cells):
    if c.cell_type=='markdown':
        assert '\\(' not in c.source and '\\[' not in c.source
        assert not any(ord(ch)<32 and ch not in '\n\t' for ch in c.source)
    elif i>=29:
        for out in c.outputs:
            if out.output_type=='stream': print('CELL',i,out.text)
print('Saved cells:',len(nb.cells))
