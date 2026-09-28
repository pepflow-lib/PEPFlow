"""Execute visible B4 discovery, then persist state in a transient workflow cell."""

import hashlib
import os
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / "supplementary" / ".runtime"
for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[name] = "1"
for name in (
    "TEMP",
    "TMP",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_CONFIG_DIR",
    "JUPYTER_RUNTIME_DIR",
):
    os.environ[name] = str(runtime / name.lower())
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
notebook = ROOT / "pgm_example_lyap.ipynb"
nb = nbf.read(notebook, as_version=4)
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Identify the vectors")
)
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Closed form")
)
source = (ROOT / "supplementary" / "b4_construct.py").read_text()
rebuild, rest = source.split("# SCAN", 1)
scan, rest = rest.split("# SEARCH", 1)
search, rest = rest.split("# BASIS", 1)
basis_source, coefficients = rest.split("# COEFFICIENTS", 1)
structure = (ROOT / "supplementary" / "b4_structure.py").read_text()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
    md(
        "## Identify the vectors composing the Lyapunov function\nWe rebuild the selected certificate and its corrected partial sums, then search for an interpretable basis. The interior domain is $1\\leq k\\leq N-1$; $k=0,N$ remain explicit exceptions, with full reconstruction required."
    ),
    code(rebuild),
    md(
        "### Candidate-vector scan\nCandidates include iterate gaps, gradients, gradient differences, composite gradients, basis vectors, tagged iterates and pairwise differences. Zero and duplicate coordinate vectors are removed."
    ),
    code(scan),
    md(
        "### Selected basis pattern\nThe sparse-basis search is executed at every nonzero-rank index, including the terminal index."
    ),
    code(search),
    md(r"""The consistent ordered interior template is
$$b_k=(r_0,r_k,a_k-a_\star,a_k),\qquad r_i=x_i-x_\star.$$
This agrees with the sparse search, up to using the readable gradient name $a_k$. At $k=0$ the basis is empty; at $k=N$ it is $(r_0)$.
"""),
    code(basis_source),
    md(
        "### Coefficient matrices\nWe use $V_k^{\\mathrm{quad}}=\\sum_{i,j}C_{ij}(k)\\langle b_{k,i},b_{k,j}\\rangle$, so off-diagonal coefficients count twice. Every numerical entry is retained, and function gaps and offsets are checked separately."
    ),
    code(coefficients),
    code(structure),
    md(r"""### Block 4 conclusion

The numerically reconstructed structure is
$$V_k=\sum_{i,j=0}^{3}c_{ij}(k,N,L)\langle b_{k,i},b_{k,j}\rangle
+\alpha(k,N)\,[f(x_k)-f(x_\star)]+\beta(k,N)\,[g(x_k)-g(x_\star)],\quad 1\leq k<N.$$
Here $c_{ij}=c_{ji}$, and the ten independent entries and the two function coefficients remain named analytic unknowns. At $k=0$, $V_0=0$. At $k=N$, the corresponding structure is
$$V_N=c_T(N,L)\|r_0\|^2+\alpha_T(N)[f(x_N)-f(x_\star)]+\beta_T(N)[g(x_N)-g(x_\star)].$$
There are no constant terms. All these sample expressions reconstruct every Gram, function-value and offset coordinate within the frozen tolerance. Numerical reconstruction does not establish an arbitrary-horizon theorem; Block 5 must derive coefficients and prove the exact step, base and terminal identities.
"""),
]
nb.cells[start:end] = cells
persist = """basis_code = BASIS_SOURCE
structure_code = 'function_coeff_by_k = '+repr(function_coeff_by_k)+'\\n\\n'+STRUCTURE_FUNCTION
unknowns = [dict(name=f'c_{i}{j}',arguments=['k','N','L'],role=f'interior.C[{i},{j}] = C[{j},{i}]',index_domain='1 <= k < N')
            for i in range(4) for j in range(i,4)]
unknowns.extend([dict(name='alpha',arguments=['k','N'],role='f gap coefficient',index_domain='1 <= k < N'),
    dict(name='beta',arguments=['k','N'],role='g gap coefficient',index_domain='1 <= k < N'),
    dict(name='c_T',arguments=['N','L'],role='terminal squared initial distance',index_domain='k=N'),
    dict(name='alpha_T',arguments=['N'],role='terminal f gap',index_domain='k=N'),
    dict(name='beta_T',arguments=['N'],role='terminal g gap',index_domain='k=N')])
expression_structure = dict(quadratic_convention='sum_ij C_ij <b_i,b_j>; C symmetric, off diagonals counted twice',
    interior=dict(index_domain='1 <= k <= N-1; exclusions a=b=1',basis_labels=['r_0','r_k','a_k-a_star','a_k'],
                  coefficients={f'{i},{j}':f'c_{i}{j}(k,N,L)' for i in range(4) for j in range(i,4)}),
    initial=dict(index_domain='k=0',basis_labels=[],expression='0'),
    terminal=dict(index_domain='k=N',basis_labels=['r_0'],coefficients={'0,0':'c_T(N,L)'}),
    function_terms=[dict(expression='f(x_k)-f(x_star)',coefficient='alpha(k,N)',index_domain='1<=k<N'),
                    dict(expression='g(x_k)-g(x_star)',coefficient='beta(k,N)',index_domain='1<=k<N'),
                    dict(expression='f(x_N)-f(x_star)',coefficient='alpha_T(N)',index_domain='k=N'),
                    dict(expression='g(x_N)-g(x_star)',coefficient='beta_T(N)',index_domain='k=N')],constant_terms=[])
state_b4 = dict(b3)
state_b4.update(basis_templates={'interior':['r_0','r_k','a_k-a_star','a_k'],'initial':[],'terminal':['r_0']},
    basis_code=basis_code,structure_code=structure_code,coeff_by_k={str(k):C.tolist() for k,C in coeff_by_k.items()},
    function_coeff_by_k={str(k):v for k,v in function_coeff_by_k.items()},coeff_code=None,
    coefficient_formula_status='unresolved',expression_structure=expression_structure,unresolved_coefficients=unknowns,
    numerical_reconstruction=dict(certificate_id=b3['certificate_id'],required_indices=list(range(N_int+1)),
       quadratic_residuals={str(k):v for k,v in coefficient_residuals.items()},component_residuals=component_residuals,
       independence={str(k):v for k,v in independence.items()},
       tolerances={'indep_tol':1e-7,'span_tol':1e-5,'component_atol':1e-5,'component_rtol':1e-5},passed=True),
    numerical_certificate_verified=True,analytic_full_pep_verified=False,lyapunov_proof_verified=False)
(notebook_dir/'state'/'pgm_b4.json').write_text(json.dumps(state_b4,indent=2,allow_nan=False))
""".replace("BASIS_SOURCE", repr(basis_source)).replace(
    "STRUCTURE_FUNCTION",
    repr(
        "def V_k_structure"
        + structure.split("def V_k_structure", 1)[1].split("component_residuals =", 1)[
            0
        ]
    ),
)
nb.cells.append(code(persist))
NotebookClient(
    nb,
    timeout=180,
    kernel_name="attempt-pgm",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nb.cells.pop()
nbf.write(nb, notebook)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(c) < 32 and c not in "\n\t" for c in cell.source)
checklist = ROOT / "supplementary" / "pgm_example_lyap_checklist.md"
lines = checklist.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(notebook.read_bytes()).hexdigest()
    elif line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B4"
    elif line.startswith("| 10 |"):
        parts = line.split("|")
        parts[3:6] = [
            " verified ",
            f" {start}-{start + len(cells) - 1} ",
            " Actual candidate scan/search, consistent basis, independence and all-index reconstruction outputs executed. ",
        ]
        lines[i] = "|".join(parts)
    elif line.startswith("| 11 |"):
        parts = line.split("|")
        parts[3:6] = [
            " pending ",
            f" {start + 8}-{start + 11} ",
            " Numerical coefficient extraction verified; closed-form formulas and exact proof pending B5. ",
        ]
        lines[i] = "|".join(parts)
checklist.write_text("\n".join(lines), encoding="utf-8")
print("B4 all-index structure checks passed; notebook and state saved.")
