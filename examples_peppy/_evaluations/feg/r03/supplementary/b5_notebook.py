import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat as nbf
root=runtime.ROOT
path=root/'feg_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
md=nbf.v4.new_markdown_cell
code=nbf.v4.new_code_cell
sources={name:(root/f'supplementary/b5_{name}.py').read_text(encoding='utf-8-sig') for name in ('exact_helpers','step','derive','base','boundary')}
theorem=r'''### Theorem
Let $A$ be monotone and $L$-Lipschitz on a finite-dimensional real Euclidean space, with $L>0$, $A(x_{\star})=0$, and $\|x_{0}-x_{\star}\|^2\le R^2$, $R\ge0$. Apply the displayed FEG updates, with the shared point $x_{1/2}=x_{0}$. For every integer $N\ge1$, write $g_{k}=A(x_{k})$ and define
$$V_{0}=0,\qquad V_{k}=\frac{2k^2}{N^2}\|g_{k}\|^2+\frac{4kL}{N^2}\langle g_{k},x_{k}-x_{0}\rangle\quad(1\le k\le N).$$
Then $V_{k+1}\le V_{k}$ for $0\le k<N$, and
$$\boxed{\|A(x_{N})\|^2\le\frac{4L^2R^2}{N^2}.}$$
This is a convergence upper bound; the numerical sweep suggests sharpness for $N\ge2$, but no all-horizon sharpness claim is made.'''
proof=r'''### Proof outline
Use the explicit potential
$$V_{k}=\frac{2k^2}{N^2}\|g_{k}\|^2+\frac{4kL}{N^2}\langle g_{k},x_{k}-x_{0}\rangle,$$
with $V_{0}=0$. Define the nonpositive interpolation residuals
$$I^{\mathrm{Lip}}_{k}=\|g_{k+1}-A(x_{k+1/2})\|^2-L^2\|x_{k+1}-x_{k+1/2}\|^2\le0,$$
$$I^{\mathrm{Mon}}_{k}=-\langle g_{k+1}-g_{k},x_{k+1}-x_{k}\rangle\le0.$$
**Base.** Since $x_{1}=x_{0}-g_{0}/L$ and $x_{1/2}=x_{0}$,
$$V_{1}-V_{0}=\frac{2}{N^2}I^{\mathrm{Lip}}_{0}\le0.$$
**Interior steps.** Substitution of the two updates gives, for $1\le k<N$,
$$V_{k+1}-V_{k}=\frac{2(k+1)^2}{N^2}I^{\mathrm{Lip}}_{k}+\frac{4Lk(k+1)}{N^2}I^{\mathrm{Mon}}_{k}\le0.$$
Both coefficients are positive on this domain. Thus $V_{N}\le V_{0}=0$.
**Boundary.** Put $r_{0}=\|x_{0}-x_{\star}\|^2-R^2\le0$, $I_{\star}=-\langle g_{N},x_{N}-x_{\star}\rangle\le0$, and
$$S_{N}=\left\|\frac{2L}{N}(x_{0}-x_{\star})-g_{N}\right\|^2\ge0.$$
Direct expansion gives
$$\|g_{N}\|^2-\frac{4L^2R^2}{N^2}=V_{N}+\frac{4L}{N}I_{\star}-S_{N}+\frac{4L^2}{N^2}r_{0}\le V_{N}\le0.$$
This proves the bound with the stated squared-distance normalization. For $N=1$, the interior-step range is empty and the same base and boundary identities apply. No division by $R$ occurs, so $R=0$ is included. The exact coordinate checks below verify each identity symbolically, independently of the numerical certificate.'''
nb.cells[1:2]=[md('## Proof Statement'),md(theorem),md(proof)]
# Show the true numerical remainder and candidate multiplier table as proof-bearing matrices.
for cell in nb.cells:
    if cell.cell_type=='code' and cell.source.startswith('basis = ctx.basis_vectors()'):
        cell.source += '\nprint("True selected numerical S:")\npf.pprint_labeled_matrix(pf.MatrixWithNames(S_array,b2["basis_vectors"],b2["basis_vectors"]))\nactive_names = [name for name,value in b2["named_dual_values"].items() if value is not None]\nmultiplier_table = np.array([[float(lambda_candidate(name,N_cert,params_cert["L"])),b2["named_dual_values"][name]] for name in active_names])\npf.pprint_labeled_matrix(pf.MatrixWithNames(multiplier_table,active_names,["candidate","selected numerical"]))'
    if cell.cell_type=='code' and cell.source.startswith('def coeff_pattern('):
        cell.source += '\nprint("Candidate coefficient matrices:")\nfor k in range(1,N_int+1):\n    pf.pprint_labeled_matrix(pf.MatrixWithNames(coeff_pattern(k,N_int,float(params_sp["L"])),V_k_basis_labels(k),V_k_basis_labels(k)))'
start=next(i for i,c in enumerate(nb.cells) if c.source.startswith('## Symbolic'))
step_setup,step_rest=sources['step'].split('V_step=',1)
newcells=[md('## Exact coefficient derivation\nThe numerical two-vector basis motivates a symbolic ansatz. The following calculation derives its coefficients from the actual one-step update and fixes the free scale through the terminal normalization.'),code('''b4 = json.loads((notebook_dir/"state/feg_b4.json").read_text())
assert b4["certificate_id"] == certificate["certificate_id"]
assert b4["numerical_reconstruction"]["certificate_id"] == certificate["certificate_id"]
assert b4["numerical_reconstruction"]["required_indices"] == list(range(N_int+1))
print("Reusing unchanged numerical structure, with reconstruction checked above.")'''),code(sources['exact_helpers']),md('### Symbolic recursion context\nThis context uses symbolic positive L, positive integer N and k, and the two FEG updates. Only the identity for 1 <= k < N is needed.'),code(step_setup),md(r'''### Coefficient equations and their solution
Write $V_{k}=a_{k}\|g_{k}\|^2+b_{k}L\langle g_{k},x_{k}-x_{0}\rangle$. Requiring $V_{k+1}-V_{k}=u_{k}I^{\mathrm{Lip}}_{k}+t_{k}L I^{\mathrm{Mon}}_{k}$ gives
$$a_{k}=\frac{k b_{k}}2,\quad b_{k+1}=\frac{k+1}{k}b_{k},\quad a_{k+1}=u_{k}=\frac{(k+1)^2}{2k}b_{k},\quad t_{k}=(k+1)b_{k}.$$
Therefore $b_{k}=c k$ and $a_{k}=c k^2/2$. Choose $c=4/N^2$ to give coefficient one on the terminal metric after completing the boundary square. The base and boundary cells verify this normalization and the initial condition exactly.'''),code(sources['derive']+'\nC_exact=sp.Matrix([[2*k_sp**2/N_sp**2,2*k_sp*L_sp/N_sp**2],[2*k_sp*L_sp/N_sp**2,0]])\npf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(C_exact,dtype=object),["g_k","x_k-x_0"],["g_k","x_k-x_0"]))'),md(r'''### Closed-form Lyapunov function
The resulting exact formula is
$$V_{0}=0,\qquad V_{k}=\frac{2k^2}{N^2}\|g_{k}\|^2+\frac{4kL}{N^2}\langle g_{k},x_{k}-x_{0}\rangle\quad(1\le k\le N).$$
There are no function-value or constant terms. The next sections verify its interior, base and boundary identities in every scalar coordinate.'''),md('## Symbolic Step Recursion Verification'),md(r'''For $1\le k<N$, verify
$$V_{k+1}-V_{k}=\frac{2(k+1)^2}{N^2}I^{\mathrm{Lip}}_{k}+\frac{4Lk(k+1)}{N^2}I^{\mathrm{Mon}}_{k}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify exactly to zero. Lipschitz continuity and monotonicity make the right-hand side nonpositive.'''),code('V_step='+step_rest),md('## Base Case and Boundary Symbolic Verification'),md(r'''At the actual shared first half-step $x_{1/2}=x_{0}$, verify
$$V_{1}-V_{0}=\frac{2}{N^2}\left(\|g_{1}-g_{0}\|^2-L^2\|x_{1}-x_{0}\|^2\right).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be exactly zero. The right side is nonpositive and $V_{0}=0$. This applies for every $N\ge1$.'''),code(sources['base']),md('### Boundary Identity Symbolic Verification'),md(r'''For every $N\ge1$, verify
$$\|g_{N}\|^2-\frac{4L^2R^2}{N^2}=V_{N}-\frac{4L}{N}\langle g_{N},x_{N}-x_{\star}\rangle-\left\|\frac{2L}{N}(x_{0}-x_{\star})-g_{N}\right\|^2+\frac{4L^2}{N^2}\left(\|x_{0}-x_{\star}\|^2-R^2\right).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be exactly zero in Gram, function-value and constant coordinates. The final three terms are nonpositive, yielding metric minus target at most $V_{N}\le0$.'''),code(sources['boundary']),md(r'''## Verified conclusion
For all integers $N\ge1$, $L>0$ and $R\ge0$ under the stated operator assumptions, the exact nonincreasing Lyapunov certificate proves
$$\|A(x_{N})\|^2\le\frac{4L^2R^2}{N^2}.$$
The symbolic step, base and boundary identities vanish in all coordinates, and every required multiplier sign and denominator condition is justified. The numerical full-PEP certificate remains separately verified; a separate global analytic lambda/S proof has not been claimed. The candidate discrepancies at the additional numerical horizon remain in the discovery record and do not enter this exact local proof.''')]
nb.cells[start:]=newcells
# Normalize simple single-letter/digit subscripts consistently in Markdown.
import re
for cell in nb.cells:
    if cell.cell_type=='markdown':
        cell.source=re.sub(r'_(?!\{)([A-Za-z0-9])',r'_{\1}',cell.source)
        assert '\\(' not in cell.source and '\\[' not in cell.source
        assert all(ord(ch)>=32 or ch in '\n\t' for ch in cell.source)
nbf.write(nb,path)
(root/'supplementary/b5-theorem.md').write_text(theorem+'\n\n'+proof,encoding='utf-8')
print('Final notebook source prepared:',len(nb.cells),'cells')
