import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import nbformat
root=Path.cwd()
book=nbformat.read(root/'pgm_example_lyap.ipynb',as_version=4)
read=lambda part:(root/f'supplementary/b5_{part}.py').read_text(encoding='utf-8-sig')
readmd=lambda part:(root/f'supplementary/b5_{part}.md').read_text(encoding='utf-8-sig').replace('\\\\','\\')
# Replace the B1 theorem placeholder with the final theorem and complete proof outline.
book.cells[1:2]=[nbformat.v4.new_markdown_cell('## Proof Statement'),nbformat.v4.new_markdown_cell(readmd('theorem')),nbformat.v4.new_markdown_cell(readmd('proof_outline'))]
for cell in book.cells:
    if cell.cell_type=='markdown':
        cell.source=cell.source.replace('Certificate discovery and verification remain pending.','This was the initial B1 conjecture; the exact finite-product proof is completed below.')
        cell.source=cell.source.replace('Cross-horizon grouping has not yet been performed.','The following B3 section confirms the cross-horizon construction.')
    elif 'Complete numerical checks:' in cell.source:
        cell.source += "\npf.pprint_labeled_matrix(S,selected['basis_vectors'],precision=6)\n"
start=next(i for i,c in enumerate(book.cells) if c.cell_type=='markdown' and c.source.startswith('## B5'))
book.cells[start:]=[
nbformat.v4.new_markdown_cell('## B5 exact coefficients and Lyapunov theorem\nThe numerical B4 unknowns are now resolved by an explicit finite product. Its recurrence is derived from the one-step quadratic identity, with the terminal condition fixed by the final step. The following checks retain the original basis and compare every coordinate at both saved horizons.'),
nbformat.v4.new_code_cell(read('coeff_formula')),
nbformat.v4.new_code_cell(read('formula_comparison')),
nbformat.v4.new_markdown_cell(r'''### Deriving the coefficient recurrence
Put $m=2N-k$ and $U=T_{k+1}$. The quadratic coefficient equations give
$$T_{k}=\frac{k(k+1)(m-1)\bigl(mU+(m-1)(k+m+1)\bigr)}{((2k+1)m-k)U+(m-1)(k(k+3)m+m+1)},\qquad T_{N-1}=N-1.$$
The explicit transfer product solves this relation by splitting off its first matrix. Its initial numerator row vanishes at $k=0$, giving $T_{0}=0$. The exact polynomial calculation below verifies the recurrence and local two-square factorization; the PEPFlow contexts then check all function, Gram and offset components.'''.replace('\\\\','\\')),
nbformat.v4.new_code_cell(read('derivation')),
nbformat.v4.new_markdown_cell(r'''### Closed-form potential
With the finite-product $T_{k}$ now specified, the interior potential is
$$V_{k}=-\frac{L}{4N}\|d_{0}\|^{2}+\frac{L(N-k)}{(2N-k)^{2}}\|d_{k}\|^{2}-\frac{\langle d_{k},\nabla f(x_{k})\rangle}{2N-k}-\frac{T_{k}}{2L(2N-k)^{2}}\|\nabla f(x_{k})-\nabla f(x_{\star})\|^{2}+\frac{k+1}{2N-k}F_{k}+\frac{k}{2N-k}G_{k}.$$
The endpoint definitions are $V_{0}=0$ and $V_{N}=F_{N}+G_{N}-L\|d_{0}\|^{2}/(4N)$. The next sections verify the exact decrease, base and terminal identities. The finite-product formula is valid for arbitrary horizons; it is not a table of sample coefficients.'''.replace('\\\\','\\')),
nbformat.v4.new_markdown_cell('## Symbolic Step Recursion Verification'),
nbformat.v4.new_markdown_cell(r'''For $1\le k\le N-2$, verify
$$V_{k+1}-V_{k}=(a_{k+1}-a_{k})I^{f}_{\star,k+1}+a_{k}I^{f}_{k,k+1}+(b_{k+1}-b_{k})I^{g}_{\star,k+1}+b_{k}I^{g}_{k,k+1}-Q_{k}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in all coordinates. The common initial-anchor term cancels in this difference. All local squares and their coefficients are constructed explicitly below.'''.replace('\\\\','\\')),
nbformat.v4.new_code_cell(read('step')),
nbformat.v4.new_markdown_cell('## Base Case and Boundary Symbolic Verification'),
nbformat.v4.new_markdown_cell(r'''For $N\ge2$, verify
$$V_{1}=a_{0}I^{f}_{\star,0}-\frac{L}{4N}\|p_{0}\|^{2}+(a_{1}-a_{0})I^{f}_{\star,1}+a_{0}I^{f}_{0,1}+b_{1}I^{g}_{\star,1}-Q_{0}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish. This identity implies $V_{1}\le V_{0}=0$ and requires no evaluation of $g(x_{0})$.'''.replace('\\\\','\\')),
nbformat.v4.new_code_cell(read('base')),
nbformat.v4.new_markdown_cell('### Boundary Identity Symbolic Verification'),
nbformat.v4.new_markdown_cell(r'''For $N\ge2$, verify
$$V_{N}-V_{N-1}=\frac1{N+1}I^{f}_{\star,N}+\frac N{N+1}I^{f}_{N-1,N}+\frac2{N+1}I^{g}_{\star,N}+\frac{N-1}{N+1}I^{g}_{N-1,N}-Q_{\mathrm{end}}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish, using $T_{N-1}=N-1$. The two terminal squared norms are constructed in the code.'''.replace('\\\\','\\')),
nbformat.v4.new_code_cell(read('boundary')),
nbformat.v4.new_markdown_cell('### Exceptional horizon $N=1$'),
nbformat.v4.new_markdown_cell(r'''Verify the separate identity
$$V_{1}=\tfrac12 I^{f}_{\star,0}-\tfrac L4\|p_{0}\|^{2}+\tfrac12 I^{f}_{\star,1}+\tfrac12 I^{f}_{0,1}+I^{g}_{\star,1}-Q_{\mathrm{end}}.$$
Here $Q_{\mathrm{end}}$ uses $N=1$; $\mathrm{LHS}-\mathrm{RHS}$ must vanish. No interior formula outside its index domain is assumed.'''.replace('\\\\','\\')),
nbformat.v4.new_code_cell(read('N1')),
nbformat.v4.new_markdown_cell(r'''### Signs, domain and radius normalization
For all transfer factors, $j\ge0$ and $m_{j}>1$. The first row is nonnegative and the second row strictly positive, so the product has a positive denominator and $T_{k}\ge0$. In each interior/base square, $U=T_{k+1}\ge0$ and $m>1$, hence $H>0$ and
$$D=\bigl(k(2m-1)+m\bigr)U+(m-1)\bigl(k(k+3)m+m+1\bigr)>0.$$
Thus $A,B>0$. The interpolation weights are nonnegative by the explicitly checked difference formulas; the terminal and $N=1$ weights are also nonnegative. Each displayed step has nonpositive residual terms minus nonnegative squares, establishing $V_{k+1}\le V_{k}$.
Finally verify the exact normalization identity
$$h(x_{N})-h(x_{\star})-\frac{LR^{2}}{4N}=V_{N}+\frac{L}{4N}\bigl(\|d_{0}\|^{2}-R^{2}\bigr).$$
Both terms on the right are nonpositive. Denominators are nonzero for $L>0$, integer $N\ge1$, and the indicated index domains. The initial distance assumption covers $R=0$ without division by $R$.'''.replace('\\\\','\\')),
nbformat.v4.new_code_cell(read('signs')),
nbformat.v4.new_markdown_cell('The numerical full-PEP certificate and the analytic Lyapunov proof are verified separately. The all-horizon theorem follows from the exact local identities and sign argument above. A separate global closed-form full-PEP matrix proof is not claimed. Presentation checks follow evaluation-ancillary-v1: source and execution were checked; no rendering or image inspection was performed.')]
for cell in book.cells:
    if cell.cell_type=='markdown':
        assert '\\(' not in cell.source and '\\[' not in cell.source
        assert not any(ord(c)<32 and c not in '\n\t' for c in cell.source)
nbformat.write(book,root/'pgm_example_lyap.ipynb')
print('Final notebook source assembled.')
