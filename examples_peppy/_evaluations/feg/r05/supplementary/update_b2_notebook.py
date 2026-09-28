import importlib.util
import json
import os
from pathlib import Path

spec = importlib.util.spec_from_file_location('runtime', Path(__file__).parent / 'helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat as nbf
from nbclient import NotebookClient

root = runtime.ROOT
path = root / 'feg_example_lyap.ipynb'
nb = nbf.read(path, as_version=4)
verify_source = (root / 'supplementary/helpers/verify_certificate.py').read_text(encoding='utf-8-sig')
verify_source = verify_source[verify_source.index('def verify_saved'):]
cells = [nbf.v4.new_markdown_cell('## Full-PEP certificate\nThe selected certificate is numerical and coherent at N=6, L=R=1. Analytic full-PEP and Lyapunov proofs remain unresolved.'),
nbf.v4.new_code_cell('''import hashlib
import numpy as np
from pepflow.utils import Comparator
b2 = json.loads((notebook_dir / "state/feg_b2.json").read_text())
dense = json.loads((notebook_dir / "state/feg_dense.json").read_text())
for relative, expected in b2["certificate_provenance"]["source_hashes"].items():
    assert hashlib.sha256((notebook_dir / relative).read_bytes()).hexdigest() == expected
print("Dense objective:", dense["opt_value"])
print("Selected objective:", b2["opt_value"])
print("Basis:", b2["basis_vectors"])
for group in dense["lambda_groups"]:
    significant = [name for name, meta in dense["constraint_metadata"].items()
                   if meta["group"] == group and abs(dense["named_dual_values"][name]) > 1e-6]
    print(group, "significant entries:", len(significant))
print("Dense S eigenvalues:", np.linalg.eigvalsh(dense["S_matrix"]))
# The relaxation drops precisely the interpolation entries below the frozen cutoff.
dropped = [name for name, value in dense["named_dual_values"].items()
           if name != "initial_condition" and abs(value) <= 1e-6]
assert dropped == b2["relaxed_constraints"]
assert abs(dense["opt_value"] - b2["opt_value"]) < 1e-5
assert abs(b2["opt_value"] - 4/b2["N"]**2) < 1e-5
print("Dropped constraints:", len(dropped), "; objective preserved.")
for name, value in b2["named_dual_values"].items():
    if value is not None:
        print(name, value)'''),
nbf.v4.new_markdown_cell(r'''### Numerical decomposition and certificate identity
The saved reversed-basis LDL factors obey $S=E^\top D E$, with all factor entries retained. Scalar constraints are normalized as $r_i\le0$; the checked identity is
$$\mathrm{metric}-\mathrm{bound}-\sum_i\lambda_i r_i+S=0.$$
We check Gram, function-value and constant coordinates, inequality signs, positive semidefiniteness, and the dense/relaxed objective gap.'''),
nbf.v4.new_code_cell(verify_source),
nbf.v4.new_code_cell('''ctx_cert, pb_cert, A_cert, pm_cert, residual_cert, checks = verify_saved(b2, dense["opt_value"])
print(checks)
D = np.asarray(b2["numerical_decomposition"]["D"])
E = np.asarray(b2["numerical_decomposition"]["ell_coords"])
pf.pprint_labeled_matrix(E, [f"ell_{i}" for i in range(len(E))], b2["basis_vectors"], precision=5)
print("LDL diagonal:", np.diag(D))
print("Off-diagonal LDL max:", np.max(np.abs(D-np.diag(np.diag(D)))))
pf.pprint_labeled_matrix(np.asarray(residual_cert.inner_prod_coords), b2["basis_vectors"], b2["basis_vectors"], precision=10)
print("Function residual:", residual_cert.func_coords, "offset:", residual_cert.offset)'''),
nbf.v4.new_markdown_cell(r'''### Initial closed-form search
The coefficient candidates at $L=R=1$ are $4k(k+1)/N^2$ for consecutive monotonicity ($1\le k<N$), $2(k+1)^2/N^2$ for half-step Lipschitz ($0\le k<N$), $4/N$ for terminal monotonicity, and $4/N^2$ for the initial condition. The proposed remainder is $\|(2/N)(x_0-x_\star)-A(x_N)\|^2$.
These plausible candidates do **not** match the selected numerical dual to the required $10^{-4}$ tolerance. They are recorded as unresolved guesses, not substituted for the saved certificate. The verified LDL decomposition supplies the numerical handoff.'''),
nbf.v4.new_code_cell('''n = b2["N"]
candidate = {"initial_condition": 4/n**2, f"A monotone:x_{n},x_star": 4/n}
for k in range(1, n):
    candidate[f"A monotone:x_{k},x_{k+1}"] = 4*k*(k+1)/n**2
for k in range(n):
    half = "x_0" if k == 0 else f"x_{k}+1/2"
    candidate[f"A Lipschitz:{half},x_{k+1}"] = 2*(k+1)**2/n**2
lambda_error = max(abs(value-candidate.get(name, 0)) for name, value in b2["named_dual_values"].items() if value is not None)
v = 2/n*(ctx_cert["x_0"]-ctx_cert["x_star"]) - A_cert(ctx_cert[f"x_{n}"])
S_guess = pm_cert.eval_scalar(v**2)
S_error = np.max(np.abs(S_guess.inner_prod_coords - np.asarray(b2["S_matrix"])))
pf.pprint_labeled_matrix(np.asarray(S_guess.inner_prod_coords), b2["basis_vectors"], b2["basis_vectors"], precision=5)
print("Lambda candidate error:", lambda_error)
print("S candidate error:", S_error)
print("Candidate S function/constant components:", S_guess.func_coords, S_guess.offset)
print("Numerical certificate verified:", checks["passed"])
print("Analytic full-PEP verified: False; Lyapunov proof verified: False")''')]
end = next(i for i, cell in enumerate(nb.cells) if cell.source.startswith('## Lyapunov partial sums'))
nb.cells[11:end] = cells
nbf.write(nb, path)
os.environ['JUPYTER_PATH'] = str(runtime.RUNTIME / 'jupyter')
NotebookClient(nb, timeout=120, kernel_name='feg-private', resources={'metadata': {'path': str(root)}}).execute()
nbf.write(nb, path)
print('B2 notebook executed.')

