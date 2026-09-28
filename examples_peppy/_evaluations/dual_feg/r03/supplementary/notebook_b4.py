"""Add the complete visible basis scan, search and reconstruction evidence."""
import inspect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "supplementary"), str(ROOT / "supplementary/helpers")]
import run_b1  # noqa: E402,F401
import nbformat as nbf  # noqa: E402
from basis_structure import basis_for, basis_labels_for, coeff_pattern, numerical_structure, reconstruct_all  # noqa: E402
from execute_notebook import execute  # noqa: E402

nb = nbf.read(ROOT / "dual_feg_example_lyap.ipynb", as_version=4)
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
scan_source = (ROOT / "supplementary/b4_discover.py").read_text()
scan_source = scan_source[scan_source.index("pairs = []"):scan_source.index("results = {}")]
cells = [md("## Identify the vectors composing the Lyapunov function\nWe return to the selected $N=4$ certificate, whose interior rank 4 was independently confirmed at $N=6$. All indices, including the zero initial potential and rank-two terminal potential, must reconstruct."),
code('import itertools\nfrom pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix\n\nb3 = json.loads((notebook_dir / "state/dual_feg_b3.json").read_text())\nassert b3["rank_search"]["status"] == "confirmed"\nrank_evidence = json.loads((notebook_dir / b3["rank_search"]["evidence_path"]).read_text())\nassert rank_evidence["summary"] == b3["rank_search"]\nreplay_certificate(b3, get_pep_setup, notebook_dir, dense["opt_value"])\nn = b3["N_verify"]\nctx, pb, _ = get_pep_setup(n, json.loads(b3["params_json"]))\npm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(b3["params_json"]))\nS_scalar, pieces = full_psd_piece(b3, ctx, pm)\nlyap, observation = build_partial_sums(b3, ctx, pb, pm, S_scalar, pieces)\nassert observation["rank_profile"] == b3["rank_profile"]\nfor k, value in enumerate(lyap):\n    evaluated = pm.eval_scalar(value)\n    assert np.allclose(np.asarray(evaluated.inner_prod_coords, dtype=float), b3["lyap_inner_prod_coords"][k], atol=1e-4, rtol=1e-5)\n    assert np.allclose(evaluated.func_coords, b3["lyap_func_coords"][k], atol=1e-4, rtol=1e-5)\n    assert np.allclose(float(evaluated.offset), b3["lyap_offsets"][k], atol=1e-4, rtol=1e-5)'),
md("### Candidate-vector scan\nCandidates include tagged iterates, operator outputs, auxiliary vectors $z_k$, all point-pair differences, and the terminal anchor displacement. Equivalent coordinates and the zero vector are removed, with meaningful derived labels preferred."),
code(scan_source),
code('in_col_by_k = {}\nfor k in range(n+1):\n    in_col = vectors_in_column_space(lyap[k], [v for _, v in unique], pep_context=ctx, resolve_parameters=params, rtol=1e-4, atol=1e-4)\n    in_col_by_k[k] = in_col\n    print(f"V_{k} column-space candidates:")\n    for v in in_col:\n        print("  ", labels[id(v)])'),
md("### Selected basis pattern\nThe following exhaustive subset search uses the framework utility and the frozen tolerances. We then adopt the uniform auxiliary-vector basis for interpretability; at $k=N-1$ the sparsest output instead uses the last current operator value. Both choices reconstruct, and the adopted basis avoids a separate penultimate case."),
code('sparse_coefficients = {}\nfor k in range(n+1):\n    sparse_basis, C = find_basis_with_sparsest_coefficients(lyap[k], in_col_by_k[k], pep_context=ctx, resolve_parameters=params, zero_tol=1e-6, indep_tol=1e-7, span_tol=1e-5)\n    assert len(sparse_basis) == b3["rank_profile"][k]\n    sparse_coefficients[k] = C\n    print(f"k={k}, rank {b3[\'rank_profile\'][k]}")\n    print("sparse basis:", [labels[id(v)] for v in sparse_basis])\n    print("zero coefficients:", int(np.sum(abs(C) < 1e-6)), "/", C.size)'),
md(r"""For $1\leq k<N$, adopt the ordered basis
$$\big[A(x_N),\ x_0-x_N,\ x_k-x_N,\ z_k\big].$$
At $k=0$ the basis is empty; at $k=N$ use $[A(x_N),x_0-x_N]$. These exceptions remain part of the reconstruction and final proof."""),
code(inspect.getsource(basis_for) + "\n" + inspect.getsource(basis_labels_for) + '\ndef V_k_basis(k):\n    return basis_for(ctx, k, n)\ndef V_k_basis_labels(k):\n    return basis_labels_for(k, n)\n\nfor k in range(n+1):\n    basis = V_k_basis(k)\n    matrix = np.column_stack([pm.eval_vector(v).coords for v in basis]).astype(float) if basis else np.empty((len(ctx.basis_vectors()), 0))\n    rank = int(np.linalg.matrix_rank(matrix, tol=1e-7)) if basis else 0\n    assert rank == len(basis) == b3["rank_profile"][k]\n    print(f"k={k}: rank {rank} basis {V_k_basis_labels(k)}")'),
md("### Coefficient matrices\n" + r"The interior order is $[A(x_N),x_0-x_N,x_k-x_N,z_k]$; the terminal order is $[A(x_N),x_0-x_N]$. The symmetric convention is $V_k=\sum_{ij}C_{ij}\langle v_i,v_j\rangle$, so off-diagonal entries contribute twice. There are no function-value or constant terms. Candidate formulas remain unproved over the full horizon and parameter domain."),
code(inspect.getsource(coeff_pattern) + "\n" + inspect.getsource(numerical_structure) + "\n" + inspect.getsource(reconstruct_all)),
code('coefficients, reconstruction, fit_errors = reconstruct_all(b3, ctx, pm, lyap)\nassert reconstruction["passed"]\nfor k, C in coefficients.items():\n    print(f"V_{k} numerical coefficient matrix")\n    if C.size:\n        pf.pprint_labeled_matrix(C, V_k_basis_labels(k), V_k_basis_labels(k), precision=6)\n        print("Candidate coefficient matrix")\n        pf.pprint_labeled_matrix(np.asarray(coeff_pattern(k, n), dtype=float), V_k_basis_labels(k), V_k_basis_labels(k), precision=6)\n    else:\n        print("Empty initial matrix")\n    evaluated = pm.eval_scalar(lyap[k])\n    print("Function-value coordinates:", list(evaluated.func_coords), "offset:", evaluated.offset)\n    print("Full-component residuals:", reconstruction["component_residuals"][str(k)])'),
md(r"""### Block 4 conclusion
The numerical matrices suggest, for $1\leq k<N$ and $g_N=A(x_N)$,
$$V_k=-\frac{4L}{N}\langle g_N,x_0-x_N\rangle+\frac{4L}{N-k}\langle g_N,x_k-x_N\rangle-4\langle g_N,z_k\rangle+\frac{4L}{N-k}\langle x_k-x_N,z_k\rangle-2\|z_k\|^2.$$
The initial potential is $V_0=0$, and the terminal candidate is
$$V_N=2\|g_N\|^2-\frac{4L}{N}\langle g_N,x_0-x_N\rangle.$$
All selected numerical partial sums reconstruct, including endpoints and all scalar components. The same template and candidate coefficients also reconstruct the $N=6$ sample within the frozen tolerances. These are candidate formulas, not yet an arbitrary-horizon theorem. Block 5 must establish exact step, base, terminal, and rate-normalization arguments."""),
code('confirmation6 = json.loads((notebook_dir / "supplementary/b2-N6.json").read_text())\nreplay_certificate(confirmation6, get_pep_setup, notebook_dir, dense6["opt_value"])\nctx6, pb6, _ = get_pep_setup(6, json.loads(confirmation6["params_json"]))\npm6 = pf.ExpressionManager(ctx6, resolve_parameters=json.loads(confirmation6["params_json"]))\nS6, pieces6 = full_psd_piece(confirmation6, ctx6, pm6)\nlyap6, observation6 = build_partial_sums(confirmation6, ctx6, pb6, pm6, S6, pieces6)\ncoefficients6, reconstruction6, fit_errors6 = reconstruct_all(confirmation6, ctx6, pm6, lyap6)\nassert reconstruction6["passed"]\nprint("All indices passed at N=4 and N=6; coefficient formulas retain candidate status.")')]
start = next(i for i, c in enumerate(nb.cells) if c.source.startswith("## Identify the vectors"))
end = next(i for i, c in enumerate(nb.cells) if c.source.startswith("## Closed-form Lyapunov"))
nb.cells[start:end] = cells
nbf.write(nb, ROOT / "dual_feg_example_lyap.ipynb")
_, evidence = execute("B4")
checklist = ROOT / "supplementary/dual_feg_example_lyap_checklist.md"
text = checklist.read_text(encoding="utf-8-sig")
text = re.sub(r"Last reviewed block: .*", "Last reviewed block: B4", text)
text = re.sub(r"SHA-256: .*", "SHA-256: " + evidence["sha256"], text)
lines = text.splitlines()
for i, line in enumerate(lines):
    if line.startswith("| 10 |"):
        p = line.split("|")
        p[3], p[4], p[5] = " verified ", f" {start}-{start+len(cells)-1} ", " Visible candidate scan, actual sparse-basis search, independence and every-index full-component reconstructions executed; two-horizon coefficient candidates checked "
        lines[i] = "|".join(p)
    elif line.startswith("| 11 |"):
        p = line.split("|")
        p[4], p[5] = f" {start+9}-{start+len(cells)-1} ", " Coefficient extraction verified; closed-form analytic proof remains pending B5 "
        lines[i] = "|".join(p)
checklist.write_text("\n".join(lines))
