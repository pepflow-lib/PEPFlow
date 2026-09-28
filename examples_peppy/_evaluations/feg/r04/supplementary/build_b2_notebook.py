import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent / 'helpers'))
import runtime
import ast
import hashlib
import json
import nbformat as nbf
from nbclient import NotebookClient
from jupyter_client import KernelManager

root=runtime.ATTEMPT
path=root/'feg_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
nb.cells[8].source=nb.cells[8].source.split('## Dense and relaxed proof solves')[0]
nb.cells=nb.cells[:9]
md=nbf.v4.new_markdown_cell
code=nbf.v4.new_code_cell
data=json.loads((root/'state/feg_b2.json').read_text())
nb.cells += [md('## Dense and relaxed proof solves\nAt $N=6$, retain the monotonicity pairs $(x_k,x_{k+1})$, $1\\leq k<N$, and $(x_N,x_\\star)$, plus the Lipschitz pairs $(x_j,x_{j-1/2})$, $1\\leq j\\leq N$. The trial drops dense multipliers smaller than $10^{-6}$ and obtains a fresh coherent primal certificate. All displayed numerical components belong to that selected solve.'),code('''import numpy as np
import hashlib
from pepflow.utils import Comparator
from certificate import digest

dense = json.loads((notebook_dir / "state/feg_dense.json").read_text())
b2 = json.loads((notebook_dir / "state/feg_b2.json").read_text())
assert b2["certificate_id"] == digest(b2)
for relative, expected in b2["certificate_provenance"]["source_hashes"].items():
    assert hashlib.sha256((notebook_dir / relative).read_bytes()).hexdigest() == expected
print("Dense:", dense["opt_value"], "Selected:", b2["opt_value"])
print("Gap:", abs(dense["opt_value"] - b2["opt_value"]))
print("Basis:", b2["basis_vectors"])
print("Dense S eigenvalues:", np.linalg.eigvalsh(dense["S_matrix"]))
for group in dense["lambda_groups"]:
    active = [(name, value) for name, value in dense["named_dual_values"].items() if dense["constraint_metadata"][name]["group"] == group and value is not None and abs(value) > 1e-6]
    print("Dense significant group", group, active)
print("Dropped constraints:", len(b2["relaxed_constraints"]))
for name, value in b2["named_dual_values"].items():
    if value is not None:
        print(name, value)
assert abs(dense["opt_value"] - b2["opt_value"]) < 1e-5
'''),md(r'''## Lambda and S verification
The numerical identity uses each inequality residual $r_c\leq0$ and the same solve's Gram remainder:
$$\|A(x_N)\|^2-\mathrm{bound}-\sum_c\lambda_c r_c+S=0.$$
The initial residual includes its constant $-R^2$. Thus nonnegative multipliers and $S\succeq0$ imply the bound. All Gram, scalar-value and offset coordinates are checked. The numerical LDL decomposition retains every factor, including small terms and any off-diagonal blocks; no small term is silently discarded.
''')]
source=(root/'supplementary/helpers/certificate.py').read_text(encoding='utf-8-sig')
tree=ast.parse(source)
functions={node.name:ast.get_source_segment(source,node) for node in tree.body if isinstance(node,ast.FunctionDef)}
nb.cells.append(code('PARAMS: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.S.One, "R": sp.S.One}\n\n'+functions['inventory']+'\n\n'+functions['verify']+'''\n\nchecks = verify(b2, dense_value=dense["opt_value"])
print(checks)
assert checks["passed"]
'''))
nb.cells.append(code('''E = np.asarray(b2["numerical_decomposition"]["ell_coords"])
D = np.asarray(b2["numerical_decomposition"]["D"])
S_saved = np.asarray(b2["S_matrix"])
print("LDL diagonal:", np.diag(D))
print("Minimum eigenvalue of D:", np.linalg.eigvalsh(D).min())
pf.pprint_labeled_matrix(pf.MatrixWithNames(E, [f"ell_{i}" for i in range(len(E))], b2["basis_vectors"]))
pf.pprint_labeled_matrix(pf.MatrixWithNames(E.T @ D @ E - S_saved, b2["basis_vectors"], b2["basis_vectors"]))
assert np.allclose(E.T @ D @ E, S_saved, atol=1e-4, rtol=1e-5)
'''))
nb.cells.append(md(r'''### Initial closed-form search
The active multipliers suggest
$$\lambda^{\rm mon}_{k,k+1}=\frac{4Lk(k+1)}{N^2},\quad\lambda^{\rm mon}_{N,\star}=\frac{4L}{N},\quad\lambda^{\rm Lip}_{j,j-1/2}=\frac{2j^2}{N^2},\quad\tau=\frac{4L^2}{N^2}.$$
The rank-one remainder suggests
$$S_{\rm candidate}=\left\|A(x_N)-\frac{2L}{N}(x_0-x_\star)\right\|^2.$$
These candidates satisfy the exact coordinate identity at $N=6$, $L=R=1$. They do **not** match every selected numerical coefficient within $10^{-4}$: the finite numerical dual has small perturbations amplified along its nearly singular optimum. Therefore the complete numerical certificate, rather than rounded candidates, is carried forward. The arbitrary-horizon identity remains unresolved here; the numerical check is not an analytic theorem.
'''))
nb.cells.append(code(data['lamb_code']+'\n'+data['S_code']))
nb.cells.append(code('''ctx, pb, A = get_pep_setup(6, PARAMS)
pm = pf.ExpressionManager(ctx, resolve_parameters=PARAMS)
entries = inventory(ctx, pb, A)
weighted = sum((candidate_lambda(c.name, 6) * (c.lhs - c.rhs) for c, *_ in entries), pf.Scalar.zero())
S_guess = candidate_S(ctx, A, 6)
exact = pm.eval_scalar(pb.performance_metric - sp.Rational(4, 36) - weighted + S_guess, sympy_mode=True)
exact_checks = {name: all(sp.simplify(v) == 0 for v in np.asarray(getattr(exact, name), dtype=object).flat) for name in ("inner_prod_coords", "func_coords", "offset")}
for group, matrix_data in b2["lambda_groups"].items():
    family = "A monotone" if group == "Monotone Operator Inequality" else "A Lipschitz"
    candidate_matrix = np.array([[candidate_lambda(f"{family}:{ri},{ci}", 6) for ci in matrix_data["col_names"]] for ri in matrix_data["row_names"]], dtype=object)
    pf.pprint_labeled_matrix(pf.MatrixWithNames(candidate_matrix, matrix_data["row_names"], matrix_data["col_names"]))
print("Exact sample coordinate checks:", exact_checks)
assert all(exact_checks.values())
pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(exact.inner_prod_coords), b2["basis_vectors"], b2["basis_vectors"]))
lambda_error = max(abs(float(candidate_lambda(name, 6)) - value) for name, value in b2["named_dual_values"].items() if value is not None)
S_candidate_array = np.asarray(pm.eval_scalar(S_guess).inner_prod_coords, dtype=float)
S_error = np.max(np.abs(S_candidate_array - S_saved))
pf.pprint_labeled_matrix(pf.MatrixWithNames(S_candidate_array, b2["basis_vectors"], b2["basis_vectors"]))
print("Candidate lambda mismatch:", lambda_error, "S mismatch:", S_error)
print("Initial search record:", b2["closed_form_search"])
print("Numerical certificate verified:", checks["passed"])
print("Analytic full-PEP verified:", b2["analytic_full_pep_verified"])
print("Lyapunov proof verified:", b2["lyapunov_proof_verified"])
'''))
nb.cells.append(md('## Partial-sum Lyapunov construction\nPending Block 3.\n\n## Identify the vectors composing the Lyapunov function\nPending Block 4.\n\n## Closed-form Lyapunov function and symbolic identities\nPending Block 5.'))
nbf.write(nb,path)
km=KernelManager(kernel_name='feg-private')
km.kernel_spec_manager.kernel_dirs=[str(runtime.RUNTIME/'jupyter/kernels')]
try:
    NotebookClient(nb,km=km,timeout=180,resources={'metadata':{'path':str(root)}}).execute()
finally:
    if km.has_kernel:
        km.shutdown_kernel(now=True)
nbf.write(nb,path)
assert not any(o.output_type=='error' for c in nb.cells if c.cell_type=='code' for o in c.outputs)
for c in nb.cells:
    if c.cell_type=='markdown':
        assert '\\(' not in c.source and '\\[' not in c.source
        assert not any(ch in c.source for ch in ('\r','\x0c','\x08'))
checkpath=root/'supplementary/feg_example_lyap_checklist.md'
text=checkpath.read_text().replace('Last reviewed block: B1','Last reviewed block: B2')
import re
text=re.sub(r'SHA-256: [a-f0-9]+','SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest(),text)
text=text.replace('| 7. dense and relaxed proof solves | pending | Later-block obligation; placeholder only |','| 7. dense and relaxed proof solves | verified | 9-10: saved dense and fresh sparse coherent solves; support, both groups, basis, eigenvalues and gap output |')
text=text.replace('| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | pending | Later-block obligation; placeholder only |','| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 11-16: full numerical identity, LDL, labeled residuals, candidate formulas and exact finite sample check; arbitrary-horizon proof explicitly unresolved |')
checkpath.write_text(text)
print('B2 notebook clean-kernel execution and source delimiter checks passed; no rendering performed.')
print('Cell count',len(nb.cells))

