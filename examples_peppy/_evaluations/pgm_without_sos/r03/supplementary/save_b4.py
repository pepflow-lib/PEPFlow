import runpy
from pathlib import Path

scope = runpy.run_path(str(Path(__file__).with_name("run_b4.py")))
import json  # noqa: E402 - imports follow runtime or notebook setup

import nbformat  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup

root = Path.cwd()
b3 = scope["b3"]
labels = ["x_0-x_star", "x_k-x_star", "grad_f(x_k)-grad_f(x_star)", "grad_f(x_star)"]
unknowns = [
    {
        "name": f"c_{i}{j}",
        "arguments": ["k", "N", "L"],
        "role": f"interior.C[{i},{j}] and symmetric counterpart",
        "index_domain": "1 <= k <= N-1",
    }
    for i in range(4)
    for j in range(i, 4)
]
unknowns += [
    {
        "name": name,
        "arguments": ["k", "N"],
        "role": role,
        "index_domain": "1 <= k <= N-1",
    }
    for name, role in [
        ("A", "coefficient of f(x_k)-f_star"),
        ("B", "coefficient of g(x_k)-g_star"),
    ]
]
unknowns += [
    {
        "name": "c_terminal",
        "arguments": ["N", "L"],
        "role": "terminal.C[0,0]",
        "index_domain": "k=N",
    }
]
structure = {
    "quadratic_convention": "sum_{i,j} C_ij <v_i,v_j>, symmetric C, off-diagonals counted twice",
    "interior": {
        "index_domain": "1 <= k <= N-1; a=b=1",
        "basis_labels": labels,
        "quadratic_coefficients": {
            f"{i},{j}": f"c_{i}{j}(k,N,L)" for i in range(4) for j in range(i, 4)
        },
    },
    "initial": {
        "index_domain": "k=0",
        "basis_labels": [],
        "quadratic_coefficients": {},
        "value": "0",
    },
    "terminal": {
        "index_domain": "k=N",
        "basis_labels": ["x_0-x_star"],
        "quadratic_coefficients": {"0,0": "c_terminal(N,L)"},
    },
    "function_terms": [
        {
            "index_domain": "1 <= k <= N-1",
            "expression": "f(x_k)-f_star",
            "coefficient": "A(k,N)",
            "candidate": "(k+1)/(2*N-k)",
        },
        {
            "index_domain": "1 <= k <= N-1",
            "expression": "g(x_k)-g_star",
            "coefficient": "B(k,N)",
            "candidate": "k/(2*N-k)",
        },
        {"index_domain": "k=N", "expression": "h(x_N)-h_star", "coefficient": "1"},
    ],
    "constant_terms": [],
}
read = lambda part: (root / f"supplementary/b4_{part}.py").read_text(  # noqa: E731 - retain the archived notebook helper
    encoding="utf-8-sig"
)
basis_code = read("basis").split("\nfor k in range")[0]
structure_code = (
    "function_coefficients = "
    + repr(scope["function_coefficients"])
    + "\n"
    + read("structure")
)
state = {
    **b3,
    "basis_templates": {"interior": labels, "initial": [], "terminal": ["x_0-x_star"]},
    "basis_code": basis_code,
    "structure_code": structure_code,
    "coeff_by_k": {str(k): C.tolist() for k, C in scope["coeff_by_k"].items()},
    "coeff_code": None,
    "coefficient_formula_status": "unresolved",
    "expression_structure": structure,
    "unresolved_coefficients": unknowns,
    "numerical_reconstruction": {
        "certificate_id": b3["certificate_id"],
        "required_indices": list(range(b3["N_verify"] + 1)),
        "quadratic_residuals": {
            str(k): v for k, v in scope["coefficient_residuals"].items()
        },
        "component_residuals": scope["component_residuals"],
        "tolerances": {
            "zero_tol": 1e-6,
            "indep_tol": 1e-7,
            "span_tol": 1e-5,
            "component_atol": 1e-4,
            "component_rtol": 1e-5,
        },
        "passed": True,
    },
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(root / "state/pgm_b4.json").write_text(json.dumps(state, indent=2))
book = nbformat.read(root / "pgm_example_lyap.ipynb", as_version=4)
start = next(
    i
    for i, c in enumerate(book.cells)
    if c.cell_type == "markdown" and c.source.startswith("## B4")
)
end = next(
    i
    for i, c in enumerate(book.cells)
    if c.cell_type == "markdown" and c.source.startswith("## B5")
)
book.cells[start:end] = [
    nbformat.v4.new_markdown_cell(
        "## Identify the vectors composing the Lyapunov function\nWe reconstruct the selected B3 sample and retain the fixed interior domain and both exceptional endpoints."
    ),
    nbformat.v4.new_code_cell(read("load")),
    nbformat.v4.new_markdown_cell(
        "### Candidate-vector scan\nCandidates include displacement anchors, gradient differences, individual smooth gradients, shifted nonsmooth subgradients, coordinate basis vectors, and pairwise iterate differences. Equal coordinate vectors and zeros are removed."
    ),
    nbformat.v4.new_code_cell(read("scan")),
    nbformat.v4.new_markdown_cell(
        "### Selected basis pattern\nThe sparse search is executed at every interior index. We adopt one consistent order across indices to expose the recurrence, and independently check its reconstruction."
    ),
    nbformat.v4.new_code_cell(read("search")),
    nbformat.v4.new_markdown_cell(r"""With $d_k=x_k-x_\star$, $p_k=\nabla f(x_k)-\nabla f(x_\star)$ and $s=\nabla f(x_\star)$, the adopted interior basis is
$$[d_0,d_k,p_k,s].$$
At $k=0$ the potential is zero and the basis is empty; at $k=N$ the quadratic basis is $[d_0]$. The selected sparse bases can change order or use $\nabla f(x_k)=p_k+s$; the adopted basis provides a consistent interpretation."""),
    nbformat.v4.new_code_cell(read("basis")),
    nbformat.v4.new_markdown_cell(
        "### Coefficient matrices\nSymmetric matrices use the displayed basis order and count off-diagonal products twice. Function gaps and scalar offsets are retained separately."
    ),
    nbformat.v4.new_code_cell(read("coefficients")),
    nbformat.v4.new_code_cell(read("structure")),
    nbformat.v4.new_markdown_cell(r"""### Block 4 conclusion
For $1\le k<N$, the observed structure is
$$V_k=\sum_{i,j=0}^3 c_{ij}(k,N,L)\langle v_i,v_j\rangle+A(k,N)(f(x_k)-f_\star)+B(k,N)(g(x_k)-g_\star),\quad v=[d_0,d_k,p_k,s].$$
The ten independent symmetric coefficients remain analytic unknowns. The function-weight candidates are $A=(k+1)/(2N-k)$ and $B=k/(2N-k)$. The initial case is $V_0=0$; the terminal case has the form $c_{\rm terminal}(N,L)\|d_0\|^2+h(x_N)-h_\star$, with candidate $c_{\rm terminal}=-L/(4N)$. Scalar offsets vanish. All indices pass numerical full-expression reconstruction. B5 must derive the remaining coefficients and prove the exact step, initial, and terminal identities; numerical reconstruction is not an analytic theorem."""),
]
nbformat.write(book, root / "pgm_example_lyap.ipynb")
print("B4 state and notebook saved.")
