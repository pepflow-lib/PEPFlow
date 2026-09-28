"""Update B2 notebook evidence without repeating solver discovery."""
import hashlib
import inspect
import json
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

from certificate_tools import check_saved, entries_for

root = Path.cwd()
path = root / "feg_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
cells = [
    nbf.v4.new_markdown_cell("## Block 2: dense and sparse certificates\nThe dense and relaxed solves were performed with the visible setup and CLARABEL defaults. Saved certificates are replayed below without a new solve. All multiplier groups, the Gram remainder, and the normalization are captured together from each primal result. The numerical certificate remains distinct from an arbitrary-horizon proof."),
    nbf.v4.new_code_cell('import numpy as np\nfrom pepflow.utils import Comparator\nfrom certificate_tools import capture\n\ndef acquire_certificate(n, dropped):\n    live_ctx, live_pb, live_obj = get_pep_setup(n, {"L": 1, "R": 1})\n    live_pb.set_relaxed_constraints(dropped)\n    return capture(live_ctx, live_pb, live_obj, {"L": 1, "R": 1})\n\ndense = json.loads((notebook_dir / "state/feg_dense.json").read_text())\nb2 = json.loads((notebook_dir / "state/feg_b2.json").read_text())\nN_int = b2["N_verify"]\nprint("Dense objective:", dense["opt_value"])\nprint("Basis:", dense["basis_vectors"])\nfor group, data in dense["lambda_groups"].items():\n    matrix = np.asarray(data["matrix"])\n    print(group, "entries > 1e-6:", int(np.sum(np.abs(matrix) > 1e-6)))\nprint("Dense S eigenvalues:", np.linalg.eigvalsh(np.asarray(dense["S_matrix"])))'),
    nbf.v4.new_code_cell('dropped = [name for name, value in dense["named_dual_values"].items()\n           if name != "initial_condition" and value is not None and abs(value) <= 1e-6]\nassert dropped == b2["relaxed_constraints"]\nprint("Dropped constraints:", len(dropped), "using threshold 1e-6")\nprint("Sparse objective:", b2["opt_value"])\nprint("Dense/sparse gap:", abs(dense["opt_value"]-b2["opt_value"]))\nassert abs(dense["opt_value"]-b2["opt_value"]) < 1e-5\nfor name, value in b2["named_dual_values"].items():\n    if value is not None:\n        print(name, value)\nctx, pb, obj = get_pep_setup(N_int, {"L": 1, "R": 1})\npb.set_relaxed_constraints(dropped)\npm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S(1), "R": sp.S(1)})'),
    nbf.v4.new_markdown_cell(r"""### Initial formula search
Rationalization suggested monotonicity weights $4k(k+1)/N^2$ for $(x_k,x_{k+1})$, terminal weight $4/N$ for $(x_N,x_\star)$, and Lipschitz weights $2k^2/N^2$ for $(x_k,x_{k-1/2})$. The $k=1$ Lipschitz pair is $(x_1,x_0)$.

The dominant rank-one remainder suggested $\|A(x_N)-2(x_0-x_\star)/N\|^2$ at $L=1$. These guesses do **not** match the selected numerical certificate within $10^{-4}$, as checked below. They are recorded for investigation, not substituted into the numerical certificate. General-$L$ scaling and arbitrary-horizon analytic validity remain unresolved."""),
    nbf.v4.new_code_cell(b2_candidate_source := 'candidate = {name: 0.0 for name in b2["named_dual_values"]}\ncandidate["initial_condition"] = 4/N_int**2\nfor k in range(1, N_int):\n    candidate[f"A monotone:x_{k},x_{k+1}"] = 4*k*(k+1)/N_int**2\ncandidate[f"A monotone:x_{N_int},x_star"] = 4/N_int\ncandidate["A Lipschitz:x_0,x_1"] = 2/N_int**2\nfor k in range(2,N_int+1):\n    candidate[f"A Lipschitz:x_{k},x_{2*k-1}/2"] = 2*k*k/N_int**2\nlambda_error = max(abs(candidate[name]-(value or 0)) for name,value in b2["named_dual_values"].items())\nS_guess = pm.eval_scalar((obj(ctx[f"x_{N_int}"])-2/N_int*(ctx["x_0"]-ctx["x_star"]))**2)\nS_array = np.asarray(b2["S_matrix"], float)\nS_guess_error = float(np.max(np.abs(S_guess.inner_prod_coords-S_array)))\nprint("Lambda candidate error:", lambda_error, "passes:", lambda_error <= 1e-4)\nprint("S candidate error:", S_guess_error, "passes:", S_guess_error <= 1e-4)\nprint("Analytic full PEP verified:", b2["analytic_full_pep_verified"])'),
    nbf.v4.new_markdown_cell(r"""### Complete numerical remainder and identity
The reverse LDL factorization retains all diagonal and off-diagonal components, including small ones. With factor rows $E$ and block-diagonal $D$, $S=E^TDE$. The signs checked below are those of the actual inequality multipliers and the complete $S$ matrix.

For residuals normalized as $r_i\le0$, the certificate identity is
$$\|A(x_N)\|^2-\mathrm{opt}-\sum_i\lambda_i r_i+\langle S,G\rangle=0.$$
The initial residual includes its constant $-R^2$. Gram, function, and offset components are all checked."""),
    nbf.v4.new_code_cell('D = np.asarray(b2["numerical_decomposition"]["D"], float)\nE = np.asarray(b2["numerical_decomposition"]["ell_coords"], float)\nS_reconstructed = E.T @ D @ E\nprint("LDL D diagonal:", np.diag(D))\nprint("Reconstruction maximum error:", np.max(np.abs(S_reconstructed-S_array)))\nassert np.allclose(S_reconstructed, S_array, atol=1e-4, rtol=1e-5)\npf.pprint_labeled_matrix(E, [f"ell_{i}" for i in range(len(E))], b2["basis_vectors"], precision=5)\npf.pprint_labeled_matrix(D, [f"ell_{i}" for i in range(len(E))], precision=5)'),
    nbf.v4.new_code_cell(inspect.getsource(entries_for) + '\n' + inspect.getsource(check_saved) + '\nchecks, identity_residual = check_saved(ctx, pb, b2, {"L": 1, "R": 1}, dense["opt_value"])\nprint(checks)\nassert checks["passed"]\npf.pprint_labeled_matrix(np.asarray(identity_residual.inner_prod_coords, float), b2["basis_vectors"], precision=9)\nprint("Function residual:", identity_residual.func_coords)\nprint("Offset residual:", identity_residual.offset)'),
    nbf.v4.new_markdown_cell("### Block 2 conclusion\nA complete, coherent numerical certificate at the selected horizon passes the fixed tolerances. The initial lambda/S search is complete, but analytic formulas remain unresolved. Blocks 3â€“4 may use the verified numerical certificate; the final analytic Lyapunov proof remains a separate obligation."),
]
for i, cell in enumerate(cells):
    cell.id = f"b2-{i:02d}"
start = next(i for i, c in enumerate(nb.cells) if c.id in ("b1-07", "b2-00"))
end = next(i for i, c in enumerate(nb.cells) if c.id == "b1-08")
nb.cells[start:end] = cells
nbf.write(nb, path)
NotebookClient(nb, timeout=120, kernel_name="attempt", resources={"metadata": {"path": str(root)}}).execute()
nbf.write(nb, path)
markdown = "\n".join(c.source for c in nb.cells if c.cell_type == "markdown")
assert not any(x in markdown for x in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r"))
checklist_path = root / "supplementary/feg_example_lyap_checklist.md"
lines = checklist_path.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B2"
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest()
    if line.startswith("| 7 |"):
        lines[i] = "| 7 | dense and relaxed proof solves | verified | b2-01, b2-02 | Saved coherent solve records, visible acquisition and sparsity recipe, gap checked. |"
    if line.startswith("| 8 |"):
        lines[i] = "| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | b2-03 through b2-08 | All active groups printed; candidate failures explicit; full LDL and coordinate identity replayed with labeled matrices. Analytic proof pending. |"
checklist_path.write_text("\n".join(lines) + "\n")
print(json.dumps({"notebook": str(path), "fresh_kernel": "passed", "math_delimiters": "passed", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}))

