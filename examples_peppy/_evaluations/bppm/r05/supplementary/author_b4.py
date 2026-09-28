"""Add the real basis search, extraction, and full expression checks to the notebook."""

from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
dest = root / "bppm_example_lyap.ipynb"
nb = nbf.read(dest, as_version=4)
scan = (root / "supplementary/b4_scan.py").read_text()
basis = (root / "supplementary/b4_basis.py").read_text()
coeff = (root / "supplementary/b4_coefficients.py").read_text()
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
cells = [
    md(
        "## Identify the vectors composing the Lyapunov function\n\nWe start from the reconstructed B3 partial sums and search for interpretable vectors spanning their quadratic parts. The retained interior indices are 1 through N-1. Both boundary indices are checked: V_0 has zero quadratic rank, and V_N is explicitly included in the search and reconstruction."
    ),
    code(
        "b3 = json.loads((notebook_dir / 'state/bppm_b3.json').read_text())\nassert b3['certificate_id'] == b2['certificate_id']\nassert certificate_checked and grouping_checked\nassert ranks == b3['rank_profile']\nassert b3['rank_search'] == rank_evidence['summary']\nfor k, Vk in enumerate(lyap):\n    actual = pm.eval_scalar(Vk)\n    for coords, saved in ((actual.inner_prod_coords, b3['lyap_inner_prod_coords'][k]), (actual.func_coords, b3['lyap_func_coords'][k]), (actual.offset, b3['lyap_offsets'][k])):\n        assert np.allclose(np.asarray(coords, dtype=float), np.asarray(saved, dtype=float), atol=1e-4, rtol=1e-5)\nprint('B3 rank and complete partial-sum coordinates revalidated at every index.')"
    ),
    md(
        r"### Candidate-vector scan"
        + "\n\n"
        + r"The candidates include $a_i=x_\star-x_i$, kernel gradients $q_i=\nabla h(x_i)$, accumulated gradient differences $q_0-q_i$, iterate differences, and the original basis vectors. Zero and duplicate coordinate vectors are removed before filtering."
    ),
    code(scan[: scan.index("spanning_by_k={}")].strip()),
    code(
        scan[
            scan.index("spanning_by_k={}") : scan.index("sparse_basis_by_k={}")
        ].strip()
    ),
    md(
        "### Selected basis pattern\n\nThe following executable search selects sparse coefficients from the actual column-space candidates at every nonzero index, including N."
    ),
    code(scan[scan.index("sparse_basis_by_k={") :].strip()),
    md(r"""The search consistently selects the point gaps and their paired kernel gradients. For comparison across $k$, we reorder the same vectors as
$$[a_0,a_k,q_0,q_k]=[x_\star-x_0,x_\star-x_k,\nabla h(x_0),\nabla h(x_k)],\qquad 1\leq k\leq N.$$
For $k=0$ the quadratic basis is empty. The chosen order separates the two point gaps from the two kernel gradients; it changes no span. Its independence and reconstruction are checked below.
"""),
    code(basis),
    md(r"""### Coefficient matrices

The basis order is $[a_0,a_k,q_0,q_k]$ for every nonzero index, including the terminal index. The convention is $\sum_{i,j}C_{ij}\langle v_i,v_j\rangle$, so off-diagonal entries count twice. Numerical function-value terms are fitted to $f(x_k)-f(x_\star)$ and $h(x_0)-h(x_k)$, and all original function coordinates and offsets remain available for the full reconstruction check.
"""),
    code(coeff[: coeff.index("def V_k_structure")].strip()),
    code(
        coeff[
            coeff.index("def V_k_structure") : coeff.index("def coeff_pattern")
        ].strip()
    ),
    md(r"""The coefficient candidate has only $C_{02}=C_{20}=1/(2\alpha N)$ and $C_{13}=C_{31}=-1/(2\alpha N)$ nonzero. The function coefficients are $k/N$ and $1/(\alpha N)$. The next check is numerical at the selected sample; it does not establish an arbitrary-horizon identity.
"""),
    code(coeff[coeff.index("def coeff_pattern") :].strip()),
    md(r"""### Block 4 conclusion

The candidate full expression is
$$V_k=\frac{k}{N}[f(x_k)-f(x_\star)]+\frac{h(x_0)-h(x_k)+\langle q_0,a_0\rangle-\langle q_k,a_k\rangle}{\alpha N}
=\frac{\alpha k[f(x_k)-f(x_\star)]+D_h(x_\star,x_k)-D_h(x_\star,x_0)}{\alpha N}.$$
It gives $V_0=0$ and applies to the terminal index as well. The numerical basis is independent and the complete expression reconstructs every selected partial sum within the frozen tolerances. There are no scalar offsets. The formula is a candidate; Block 5 must establish the exact step, base and terminal identities and signs for the stated parameter domain.
"""),
]
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown"
    and c.source.startswith("## Identify the vectors composing")
)
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Closed-form Lyapunov")
)
nb.cells[start:end] = cells
nbf.write(nb, dest)
print("B4 notebook cells:", start, "through", start + len(cells) - 1)
