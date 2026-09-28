"""Finalize theorem and exact proof cells while retaining discovery evidence."""
import json
import re
from pathlib import Path
import nbformat
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"dual_feg_example_lyap.ipynb"
nb=nbformat.read(p,as_version=4)
texts=json.loads((ROOT/"supplementary/b5-cell-sources.json").read_text(encoding="utf-8-sig"))
md=nbformat.v4.new_markdown_cell
code=nbformat.v4.new_code_cell
nb.cells[1:2]=[md("## Proof Statement"),md(texts["theorem"]),md(texts["outline"])]
for c in nb.cells:
    if c.cell_type=="code" and c.source.startswith('D = np.asarray(certificate["numerical_decomposition"]'):
        c.source='pf.pprint_labeled_matrix(S_array,row_labels=certificate["basis_vectors"],column_labels=certificate["basis_vectors"])\n'+c.source
    if c.cell_type=="code" and c.source.startswith("def coeff_pattern"):
        c.source=c.source.replace('candidate = coeff_pattern(k,N_int)','candidate = coeff_pattern(k,N_int)\n    if candidate.size:\n        pf.pprint_labeled_matrix(candidate,row_labels=V_k_basis_labels(k),column_labels=V_k_basis_labels(k))')
index=next(i for i,c in enumerate(nb.cells) if c.source.startswith("## Exact Lyapunov theorem"))
cells=[
md("## Exact coefficient formulas and symbolic contexts"),
md(r"""Restoring the parameter $L$ multiplies each iterate-gap coefficient by $L$. In the ordered interior basis $(a,z_{k},x_{k}-x_{N},x_{0}-x_{N})$, the exact coefficient matrix is
$$C_{k}=\begin{pmatrix}0&-2&2L/(N-k)&-2L/N\\-2&-2&2L/(N-k)&0\\2L/(N-k)&2L/(N-k)&0&0\\-2L/N&0&0&0\end{pmatrix}.$$
The terminal matrix on $(a,x_{0}-x_{N})$ is $\begin{pmatrix}2&-2L/N\\-2L/N&0\end{pmatrix}$, and $V_{0}=0$. These reuse the numerical candidate's structure. The exact identities below establish the formulas over their full domain. No function-value or constant terms occur."""),
code(texts["preamble"]),
code("""k_formula,N_formula = sp.symbols("k N",integer=True)
L_formula = sp.Symbol("L",positive=True)
C_formula = sp.Matrix([[0,-2,2*L_formula/(N_formula-k_formula),-2*L_formula/N_formula],
    [-2,-2,2*L_formula/(N_formula-k_formula),0],
    [2*L_formula/(N_formula-k_formula),2*L_formula/(N_formula-k_formula),0,0],
    [-2*L_formula/N_formula,0,0,0]])
pf.pprint_labeled_matrix(np.asarray(C_formula.tolist(),dtype=object),
    row_labels=["a","z_{k}","x_{k}-x_{N}","x_{0}-x_{N}"])
print("Coefficient domain: L>0, integers N>=1 and 0<k<N.")"""),
md("## Symbolic Step Recursion Verification"),
md(r"""For $t=N-k\geq2$, verify
$$V_{k+1}-V_{k}=\frac{2}{t^{2}}\left(\|A(x_{k})-A(y_{k})\|^{2}-L^{2}\|x_{k}-y_{k}\|^{2}\right)-\frac{4L}{t(t-1)}\langle a-A(y_{k}),x_{N}-y_{k}\rangle.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero in every scalar coordinate. The context keeps $N,t,L$ symbolic and substitutes the actual updates."""),
code(texts["step"]),
md("## Base Case and Boundary Symbolic Verification"),
md(r"""For every $N\geq1$, verify $V_{0}=0$ by substituting $x=x_{0}$, $z_{0}=0$, and $t=N$. The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish exactly. This calculation does not substitute into the singular terminal formula."""),
code(texts["base"]),
md("### Final-Step Identity Symbolic Verification"),
md(r"""The update with $t=1$ gives $x_{N}=x_{N-1}-(z_{N-1}+A(x_{N-1}))/L$. Verify
$$V_{N}-V_{N-1}=2\left(\|A(x_{N-1})-A(x_{N})\|^{2}-L^{2}\|x_{N-1}-x_{N}\|^{2}\right).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish. This also covers $N=1$."""),
code(texts["last"]),
md("### Boundary Identity Symbolic Verification"),
md(r"""Using $a=A(x_{N})$, $d=x_{0}-x_{\star}$, and $A(x_{\star})=0$, verify
$$\|a\|^{2}-\frac{4L^{2}}{N^{2}}\|d\|^{2}
=V_{N}-\frac{4L}{N}\langle a,x_{N}-x_{\star}\rangle-\left\|a-\frac{2L}{N}d\right\|^{2}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in Gram, function, and constant components."""),
code(texts["boundary"]),
md("### Signs, domain, and conclusion"),
md(r"""Interior denominators satisfy $t\geq2$ and $t-1\geq1$. With $L>0$, $N\geq1$, the multipliers $2/t^{2}$, $4L/[t(t-1)]$, $2$, and $4L/N$ are positive. Lipschitz and monotone residuals are nonpositive, and the boundary square is nonnegative in a real Euclidean space. Hence
$$V_{N}\leq V_{0}=0,\qquad \|A(x_{N})\|^{2}\leq\frac{4L^{2}}{N^{2}}\|x_{0}-x_{\star}\|^{2}\leq\frac{4L^{2}R^{2}}{N^{2}}.$$
All identities hold for arbitrary dimension and horizon. The numerical full-PEP certificate remains recorded separately; no independent universal global multiplier-table verification is claimed."""),
code(texts["signs"]),
]
nb.cells[index:index+1]=cells
# Brace simple Markdown subscripts consistently, without changing code.
for c in nb.cells:
    if c.cell_type=="markdown":
        c.source=re.sub(r"_([A-Za-z0-9])",r"_{\1}",c.source)
        assert "\\(" not in c.source and "\\[" not in c.source
        assert not any(ord(ch)<32 and ch not in "\n\t" for ch in c.source)
nb.metadata["kernelspec"]={"name":"attempt","display_name":"Attempt Python","language":"python"}
nbformat.write(nb,p)
print("Final proof cells:",index,len(nb.cells)-1)

