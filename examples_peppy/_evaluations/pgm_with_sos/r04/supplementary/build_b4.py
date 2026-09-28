import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json
import os

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ROOT
b3 = json.loads((root / "state/pgm_b3.json").read_text())
namespace = {"notebook_dir": root}
exec((root / "pgm_setup.py").read_text(), namespace)
exec(
    "import numpy as np\nimport sympy as sp\nimport json\n"
    + b3["S_code"]
    + "\ndef maxabs(x):\n    return float(np.max(np.abs(np.asarray(x,dtype=float)),initial=0))",
    namespace,
)
exec((root / "supplementary/b3_notebook_code.py").read_text(), namespace)
source = (root / "supplementary/b4_notebook_cells.py").read_text(encoding="utf-8-sig")
exec(source, namespace)
basis_code = source.split("# SECTION basis_definition")[1].split(
    "for k in range(N_int+1):"
)[0]
structure_code = source.split("# SECTION structure")[1].split("component_residuals =")[
    0
]
coeff_code = source[
    source.index("def coeff_pattern") : source.index(
        "for k in range(N_int+1):\n    predicted"
    )
]
state = {
    **b3,
    "basis_templates": {
        "initial": [],
        "interior": ["x_0-x_star", "x_k-x_star", "a_k-a_star", "a_k"],
        "terminal": ["x_0-x_star"],
    },
    "basis_code": basis_code,
    "structure_code": structure_code,
    "coeff_by_k": {str(k): v.tolist() for k, v in namespace["coeff_by_k"].items()},
    "coeff_code": coeff_code,
    "coefficient_formula_status": "candidate",
    "expression_structure": {
        "quadratic_convention": "sum_i,j C_ij <v_i,v_j>, symmetric C, off-diagonal counted twice",
        "interior": {
            "index_domain": "1 <= k <= N-1",
            "basis_labels": ["x_0-x_star", "x_k-x_star", "a_k-a_star", "a_k"],
            "coefficients": {
                "C00": "-L/(4*N)",
                "C11": "L*(N-k)/(2*N-k)^2",
                "C22": "1/(2*L*(2*N-k))",
                "C13=C31": "-1/(2*(2*N-k))",
                "other_entries": "0",
            },
        },
        "initial": {"index_domain": "k=0", "basis_labels": [], "coefficients": {}},
        "terminal": {
            "index_domain": "k=N",
            "basis_labels": ["x_0-x_star"],
            "coefficients": {"C00": "-L/(4*N)"},
        },
        "function_terms": [
            {
                "expression": "f(x_k)-f(x_star)",
                "coefficient": "(k+1)/(2*N-k) for 1<=k<N; 1 at k=N; 0 at k=0",
            },
            {
                "expression": "g(x_k)-g(x_star)",
                "coefficient": "k/(2*N-k) for 1<=k<N; 1 at k=N; 0 at k=0",
            },
        ],
        "constant_terms": [],
    },
    "unresolved_coefficients": [],
    "numerical_reconstruction": {
        "certificate_id": b3["certificate_id"],
        "required_indices": list(range(b3["N_verify"] + 1)),
        "quadratic_residuals": namespace["coefficient_residuals"],
        "component_residuals": namespace["component_residuals"],
        "tolerances": {
            "indep_tol": 1e-7,
            "span_tol": 1e-5,
            "component_atol": 1e-4,
            "component_rtol": 1e-5,
        },
        "passed": True,
    },
    "basis_search": namespace["search_results"],
    "lyapunov_proof_verified": False,
}
(root / "state/pgm_b4.json").write_text(json.dumps(state, indent=2, allow_nan=False))
path = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Identify the vectors")
)
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Symbolic step")
)
sections = source.split("# SECTION ")
new = [
    nbformat.v4.new_markdown_cell(
        "## Identify the vectors composing the Lyapunov function\nReplay the selected coherent B3 certificate and partial sums. The fixed rank-comparison exclusions are (1,1); both endpoints still require reconstruction."
    ),
    nbformat.v4.new_code_cell(sections[0]),
]
headings = {
    "candidate_scan": "### Candidate-vector scan\nScan tagged iterate gaps, gradients, proximal displacements, basis vectors and pairwise differences; remove zero and duplicate coordinates.",
    "basis_search": "### Selected basis pattern\nThe actual sparsity search below is followed by a consistent ordered basis. The ordered basis is preferred for a common iteration formula and is independently reconstructed.",
    "basis_definition": r"For $1\leq k<N$, use $[x_0-x_\star,\ x_k-x_\star,\ a_k-a_\star,\ a_k]$. At $k=0$ the basis is empty; at $k=N$ it is $[x_0-x_\star]$.",
    "coefficients": "### Coefficient matrices\nAll indices, including initial and terminal cases, are reconstructed in the stated basis order. Off-diagonal entries contribute twice.",
    "structure": "Full-expression reconstruction retains the observed function gaps and scalar offsets. The subsequent coefficient formulas are numerical candidates only.",
}
for section in sections[1:]:
    key, code = section.split("\n", 1)
    new += [
        nbformat.v4.new_markdown_cell(headings[key]),
        nbformat.v4.new_code_cell(code),
    ]
new.append(
    nbformat.v4.new_markdown_cell(r"""### Block 4 conclusion
The reconstructed interior structure is
$$V_k=-\frac{L}{4N}\|x_0-x_\star\|^2+\frac{L(N-k)}{(2N-k)^2}\|x_k-x_\star\|^2+\frac{\|a_k-a_\star\|^2}{2L(2N-k)}-\frac{\langle x_k-x_\star,a_k\rangle}{2N-k}+\frac{k+1}{2N-k}(f_k-f_\star)+\frac{k}{2N-k}(g_k-g_\star).$$
The exceptional cases are $V_0=0$ and $V_N=h_N-h_\star-\frac{L}{4N}\|x_0-x_\star\|^2$. Every numerical component reconstructs. The displayed coefficients are candidates; Block 5 must prove the step, initial, and terminal identities for arbitrary horizons and justify their signs.""")
)
nb.cells[start:end] = new
nbformat.write(nb, path)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(
    nb,
    timeout=240,
    kernel_name="attempt-python",
    resources={"metadata": {"path": str(root)}},
).execute()
nbformat.write(nb, path)
print("B4 notebook clean-kernel execution passed; cell count", len(nb.cells))
