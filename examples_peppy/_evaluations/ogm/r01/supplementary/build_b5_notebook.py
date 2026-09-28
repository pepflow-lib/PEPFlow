import sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'supplementary/helpers'))
import runtime
import re
import nbformat

path=root/'ogm_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
m,c=nbformat.v4.new_markdown_cell,nbformat.v4.new_code_cell
# Preserve the original diagnostic trail and add the missing true-S display.
nb.cells[15].source += '\nprint("Saved numerical Gram matrix:")\npf.pprint_labeled_matrix(np.asarray(b2["S_matrix"],dtype=float),b2["basis_vectors"],precision=7)\n'
nb.cells[35].source += '''
for k in range(N_int+1):
    C_guess, alpha_guess = coeff_pattern(k, N_int)
    if C_guess.size:
        print("Candidate closed-form coefficient matrix at k=", k)
        pf.pprint_labeled_matrix(C_guess, V_k_basis_labels(k), precision=8)
    print("Candidate function coefficient:", alpha_guess)
'''
nb.cells=nb.cells[:1]+[m('## Proof Statement'),m((root/'supplementary/b5_theorem.md').read_text(encoding='utf-8-sig')),m((root/'supplementary/b5_proof_outline.md').read_text(encoding='utf-8-sig'))]+nb.cells[2:37]
nb.cells += [m('## Exact coefficient derivation and proof domain'),m(r'''The numerical matrices suggested the coefficients, but the following calculation establishes them over the full domain. Let $\Phi_{k}=A_{k}(f(x_{k})-f_{\star})+B_{k}\|g_{k}\|^2+C\|z_{k+1}-x_{\star}\|^2$. The selected formulas are $A_{k}=2\theta_{k}^{2}$, $B_{k}=-\theta_{k}^{2}/L$, and $C=L/2$. Matching function-value coefficients in the step identity forces the consecutive multiplier $A_{k}=2\theta_{k}^{2}$ and star multiplier $A_{k+1}-A_{k}=2\theta_{k+1}$. The last equality follows from the ordinary recurrence. At the terminal step the coefficient becomes $A_{N}=T^{2}$, so the star multiplier is $T^{2}-2\theta_{N-1}^{2}=T$. The checks below verify all remaining quadratic and constant coefficients, rather than relying on the fit.

The resulting closed form is $V_{0}=0$ and $V_{k}=(\Phi_{k}-L\|x_{0}-x_{\star}\|^{2}/2)/T^{2}$ for $1\leq k\leq N$, with the full interior and terminal $\Phi_{k}$ given in the proof outline. The local symbolic parameters $t,s$ stand for consecutive theta values; polynomial reduction uses exactly $t^{2}=s^{2}-s$ or $2t^{2}=s^{2}-s$. Denominators are nonzero because $L>0$ and all theta values used here are positive.'''),c('''with (notebook_dir / "state/ogm_b4.json").open() as stream:
    b4 = json.load(stream)
assert certificate_digest(b4) == b4["certificate_id"]
assert b4["numerical_reconstruction"]["certificate_id"] == b4["certificate_id"]
assert set(component_residuals) == {str(k) for k in range(N_int+1)}
assert all(max(values.values()) < 1e-4 for values in component_residuals.values())
print("Same-certificate B4 structure rechecked above; now proving the symbolic identities.")'''),c((root/'supplementary/b5_symbolic_helpers.py').read_text(encoding='utf-8-sig').replace('import sympy as sp\n','')),m('## Symbolic Step Recursion Verification'),m(r'''For $0\leq j\leq N-2$, the identity is
$$\Phi_{j+1}-\Phi_{j}=2s\mathcal I_{\star,j+1}+2t^{2}\mathcal I_{j,j+1},\qquad t=\theta_{j},\ s=\theta_{j+1},\ t^{2}=s^{2}-s.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in every Gram, function, and constant coordinate.'''),c((root/'supplementary/b5_step.py').read_text(encoding='utf-8-sig')),m('## Base Case and Boundary Symbolic Verification'),m(r'''With $\theta_{0}=1$ and $z_{0}=x_{0}$,
$$\Phi_{0}-\frac{L}{2}\|x_{0}-x_{\star}\|^{2}=2\mathcal I_{\star,0}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish. Since the right side is nonpositive, this initializes the decrease argument.'''),c((root/'supplementary/b5_base.py').read_text(encoding='utf-8-sig')),m('### Boundary Identity Symbolic Verification'),m(r'''The special terminal recurrence gives $2t^{2}=s^{2}-s$ and
$$\Phi_{N}-\Phi_{N-1}=s\mathcal I_{\star,N}+2t^{2}\mathcal I_{N-1,N},\qquad t=\theta_{N-1},\ s=\theta_{N}.$$
The terminal metric identity is
$$\Phi_{N}-s^{2}(f(x_{N})-f_{\star})=\frac{L}{2}\left\|z_{N}-x_{\star}-\frac{s}{L}g_{N}\right\|^{2}\geq0.$$
Each residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish. The nonnegative square is subtracted when solving for the objective gap.'''),c((root/'supplementary/b5_terminal.py').read_text(encoding='utf-8-sig')),m('### Small horizon and radius normalization'),m(r'''For $N=1$, $\theta_{0}=1$, $\theta_{1}=2$, and $x_{1}=x_{0}-3g_{0}/(2L)$. The direct identity is
$$\Phi_{1}-\frac{L}{2}\|x_{0}-x_{\star}\|^{2}=2\mathcal I_{\star,0}+2\mathcal I_{\star,1}+2\mathcal I_{0,1}.$$
The normalization identity is
$$\frac{L}{2T^{2}}\|x_{0}-x_{\star}\|^{2}-\frac{LR^{2}}{2T^{2}}=\frac{L}{2T^{2}}\left(\|x_{0}-x_{\star}\|^{2}-R^{2}\right)\leq0.$$
Both residuals must vanish; no division by $R$ is used, so $R=0$ is included.'''),c((root/'supplementary/b5_small_normalization.py').read_text(encoding='utf-8-sig')),m('### Signs, domain, and telescoping conclusion'),m(r'''By induction from $\theta_{0}=1$, every ordinary theta is at least one. Since $\theta_{N-1}\geq1$, the terminal root is at least two. Thus all local multipliers $2\theta_{j+1}$, $2\theta_{j}^{2}$, and $\theta_{N}$ are positive; $L/2$ and $1/T^{2}$ are positive. The smooth convex interpolation residuals are nonpositive. Consequently $\Phi_{N}\leq\Phi_{N-1}\leq\cdots\leq\Phi_{0}\leq L\|x_{0}-x_{\star}\|^{2}/2$. The explicitly defined $V_{0},\ldots,V_{N}$ are therefore nonincreasing. The terminal square and initial radius yield
$$f(x_{N})-f(x_{\star})\leq\frac{LR^{2}}{2\theta_{N}^{2}}.$$
All local identities were checked exactly for arbitrary admissible theta pairs and $L>0$. Numerical certificate verification, global analytic full-PEP verification, and local analytic Lyapunov verification are separate statuses: the first and third are established; a separate global analytic table proof is not claimed.'''),c('''assert set(symbolic_results) == {"step","base","terminal_step","boundary","N1","normalization"}
assert all(all(parts.values()) for parts in symbolic_results.values())
print("Exact symbolic checks:", symbolic_results)
print("Numerical certificate: verified; analytic Lyapunov proof: verified.")
print("Separate global analytic full-PEP table proof: not claimed.")''')]
# Normalize unbraced simple subscripts/superscripts in Markdown only.
for cell in nb.cells:
    if cell.cell_type=='markdown':
        cell.source=re.sub(r'_\\([A-Za-z]+)',lambda match:'_{'+chr(92)+match.group(1)+'}',cell.source)
        cell.source=re.sub(r'_([A-Za-z0-9])',r'_{\1}',cell.source)
        cell.source=re.sub(r'\^([A-Za-z0-9])',r'^{\1}',cell.source)
        assert not any(ch in cell.source for ch in ('\t','\r','\f','\x08'))
        assert cell.source.count('$')%2==0
nbformat.write(nb,path)
print('Final notebook source assembled; execution follows static checks.')
