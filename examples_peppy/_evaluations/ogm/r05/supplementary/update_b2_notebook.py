"""Append B2 certificate evidence and visible replay checks to the notebook."""

import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
path = root / "ogm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
b2 = json.loads((root / "state/ogm_b2.json").read_text())
source = (root / "supplementary/helpers/certificate.py").read_text()
visible_verifier = source[source.index("def inventory(") : source.index("def capture(")]
nb.cells[-1].source = nb.cells[-1].source.split("## Full-PEP certificate")[0]
nb.cells += [
    md(r"""## Full-PEP certificate
The dense and selected sparse primal PEPs were solved separately at $N=4$, $L=R=1$, with CLARABEL defaults. The saved selected sample contains all multipliers, the Gram slack $S$, normalization, coordinate labels and source hashes from one solve. The cells below replay the complete identity without another optimization.

The dense pattern suggests retaining only $f:x_\star,x_i$ and $f:x_i,x_{i+1}$. In framework labels, $x_0$ has the alias `z_0` because $z_0=x_0$."""),
    code(
        "import hashlib\nimport numpy as np\nfrom certificate import digest_state\n\ndense = json.loads((notebook_dir / 'state/ogm_dense.json').read_text())\nb2 = json.loads((notebook_dir / 'state/ogm_b2.json').read_text())\nassert digest_state(b2) == b2['certificate_id']\nfor relpath, expected in b2['certificate_provenance']['source_hashes'].items():\n    assert hashlib.sha256((notebook_dir / relpath).read_bytes()).hexdigest() == expected\nprint('Dense objective:', dense['opt_value'])\nprint('Basis vectors:', dense['basis_vectors'])\nprint('Dense S eigenvalues:', np.linalg.eigvalsh(dense['S_matrix']))\nfor name, val in dense['named_dual_values'].items():\n    if val is not None and abs(val) > 1e-6:\n        print(name, val)"
    ),
    code(
        "N = b2['N_verify']\ntags = ['z_0'] + [f'x_{i}' for i in range(1, N + 1)]\nkeep = {f'f:{tags[i]},{tags[i+1]}' for i in range(N)}\nkeep |= {f'f:x_star,{tag}' for tag in tags}\nrelaxed = [name for name, meta in dense['constraint_metadata'].items()\n           if meta['origin'] == 'interpolation' and name not in keep]\nassert relaxed == b2['relaxed_constraints']\nprint('Dropped constraints:', len(relaxed))\nprint('Selected objective:', b2['opt_value'])\nprint('Preserved optimum difference:', abs(b2['opt_value'] - dense['opt_value']))\nassert abs(b2['opt_value'] - dense['opt_value']) < 1e-5\nfor name, val in b2['named_dual_values'].items():\n    if val is not None:\n        print(name, val)"
    ),
    md(r"""### Initial closed-form candidates
The stationary-point multipliers divided by $\theta_i$, and consecutive multipliers divided by $\theta_i^2$, have the same numerical normalization. This suggests
$$\lambda_{\star,i}=\frac{2\theta_i}{\theta_N^2}\ (i<N),\quad
\lambda_{\star,N}=\frac1{\theta_N},\quad
\lambda_{i,i+1}=\frac{2\theta_i^2}{\theta_N^2},$$
with other interpolation multipliers zero. The nearly rank-one Gram slack suggests
$$S(G)=\frac{L}{2\theta_N^2}\left\|z_N-x_\star-\frac{\theta_N}{L}g_N\right\|^2.$$
These formulas are numerical candidates. Their all-horizon identities and domain conditions have not yet been established. No target-specific reference source was consulted."""),
    code(b2["lamb_code"] + "\n" + b2["S_code"]),
    code(
        "theta = theta_sequence(N)\nlabels = b2['lambda_row_names']\ncandidate_lambda = np.array([[lamb(ri, ci, N, theta) for ci in b2['lambda_col_names']] for ri in labels])\nobserved_lambda = np.asarray(b2['lambda_matrix'], dtype=float)\n# Dropped interpolation entries have display NaNs; the complete named map records None.\nactive = np.isfinite(observed_lambda)\nassert np.allclose(candidate_lambda[active], observed_lambda[active], atol=1e-4, rtol=0)\nfor i, ri in enumerate(labels):\n    for j, ci in enumerate(b2['lambda_col_names']):\n        if f'f:{ri},{ci}' in b2['relaxed_constraints']:\n            assert candidate_lambda[i, j] == 0\nprint('Maximum active lambda formula discrepancy:', np.max(np.abs(candidate_lambda[active] - observed_lambda[active])))\npf.pprint_labeled_matrix(candidate_lambda, labels, b2['lambda_col_names'], precision=6)"
    ),
    code(visible_verifier),
    code(
        "ctx2, pb2, obj2 = get_pep_setup(N, {'L': 1, 'R': 1})\npb2.set_relaxed_constraints(b2['relaxed_constraints'])\nchecks_b2, residual_b2 = verify_certificate(ctx2, pb2, b2, dense['opt_value'])\nassert checks_b2['passed']\nprint('Complete numerical certificate:', checks_b2)\npf.pprint_labeled_matrix(np.array(residual_b2['gram']), b2['basis_vectors'], precision=10)\nprint('Function residual:', residual_b2['func'])\nprint('Offset residual:', residual_b2['offset'])"
    ),
    code(
        "pm2 = pf.ExpressionManager(ctx2, resolve_parameters=json.loads(b2['params_json']))\nS_candidate_value = scalar_coordinates(pm2, S_guess(ctx2, obj2, N, theta, 1))\nS_saved = np.asarray(b2['S_matrix'], dtype=float)\nS_candidate_array = np.asarray(S_candidate_value['gram'], dtype=float)\nassert np.allclose(S_candidate_array, S_saved, atol=1e-4, rtol=0)\nassert np.max(np.abs(S_candidate_value['func'])) == 0 and S_candidate_value['offset'] == 0\nprint('S candidate discrepancy:', np.max(np.abs(S_candidate_array - S_saved)))\npf.pprint_labeled_matrix(S_candidate_array, b2['basis_vectors'], precision=6)\nD = np.asarray(b2['numerical_decomposition']['D'], dtype=float)\nE = np.asarray(b2['numerical_decomposition']['ell_coords'], dtype=float)\nprint('Selected reverse-LDL diagonal:', np.diag(D))\nprint('Full LDL reconstruction error:', np.max(np.abs(E.T @ D @ E - S_saved)))\nassert np.allclose(E.T @ D @ E, S_saved, atol=1e-4, rtol=1e-5)\n# Retain every LDL entry, including numerical small factors.\npf.pprint_labeled_matrix(E, [f'ell_{i}' for i in range(len(E))], b2['basis_vectors'], precision=6)"
    ),
    md(r"""### B2 conclusion
All selected inequality multipliers and $S$ satisfy the numerical cone checks. Normalizing interpolation and initial constraints to $R_c\leq0$, the verified identity is
$$f(x_N)-f(x_\star)-\operatorname{opt}-\sum_c d_c R_c+S(G)=0.$$
The identity is checked in Gram, function-value and constant coordinates. Since $d_c\geq0$ and $S(G)\geq0$, this gives the bound numerically at the selected sample. The candidate formulas match this certificate, while the complete numerical LDL factors remain authoritative for subsequent replay. Numerical certificate: verified. Analytic full-PEP and Lyapunov proofs: pending.

## Lyapunov partial sums and rank profile
Pending Block 3.

## Identify the vectors composing the Lyapunov function
Pending Block 4.

## Closed-form Lyapunov function and exact proof
Pending Block 5."""),
]
nbformat.write(nb, path)
print("Notebook updated through B2.")
