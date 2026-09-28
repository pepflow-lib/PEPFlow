"""Show the actual partial-sum construction and incomplete comparison status."""
from pathlib import Path
import nbformat as nbf

root=Path(__file__).resolve().parents[1]
dest=root/'bppm_example_lyap.ipynb'
nb=nbf.read(dest,as_version=4)
md=nbf.v4.new_markdown_cell
code=nbf.v4.new_code_cell
cells=[md(r"""## Lyapunov partial sums

Let $r^f_{i,j}=f(x_j)-f(x_i)+\langle\nabla f(x_j),x_i-x_j\rangle\leq0$ and define $r^h_{i,j}$ similarly. The numerical partial sum starts at $V_0=0$. At each step it accumulates the saved weighted terms
$$V_{k+1}-V_k=d^f_{\star,k+1}r^f_{\star,k+1}
+d^f_{k,k+1}r^f_{k,k+1}
+d^h_{k+1,k}r^h_{k+1,k}
+d^h_{k,k+1}r^h_{k,k+1},$$
where the second and fourth terms are absent for $k=0$. All coefficients are nonnegative, giving the required nonincreasing direction. The complete $S$ is retained as one PSD boundary piece, together with $d^h_{\star,N}r^h_{\star,N}$. There are no omitted contributions.

The first trial uses $N=4$. Rank and coverage at this horizon are discovery evidence; comparison with a second independently solved horizon is still required.
"""),code("certificate = b2\nN_int = N\nparams_sp = params\nREPO_ROOT = repo_root"),
code((root/'supplementary/b3_certificate_check.py').read_text()),
code((root/'supplementary/b3_decomposition.py').read_text()),
code((root/'supplementary/b3_grouping.py').read_text()),
md("### Cross-horizon status\n\nAt N=4 the ranks are [0, 4, 4, 4, 4], with absolute rank tolerance 1e-4 on unscaled matrices in the original coordinate order. Fixed exclusions (1, 1) retain three indices. Full-coordinate coverage and increment identities pass. B3 is incomplete until the same recipe is checked at another horizon; B2 will acquire a coherent N=6 certificate.")]
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Lyapunov partial sums'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Identify the vectors composing'))
nb.cells[start:end]=cells
nbf.write(nb,dest)
print('B3 trial source placed in notebook.')
