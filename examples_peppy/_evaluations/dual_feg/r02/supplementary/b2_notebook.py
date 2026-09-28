import importlib.util
import json
import hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',root/'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat as nbf
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client import KernelManager
path=root/'dual_feg_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
verify=(root/'supplementary/b2_verify.py').read_text(encoding='utf-8-sig').split('# BEGIN NOTEBOOK VERIFICATION',1)[1].split('# END NOTEBOOK VERIFICATION',1)[0].strip()
summary='''import hashlib
import numpy as np
from fractions import Fraction
b2 = json.loads((notebook_dir / "state/dual_feg_b2.json").read_text())
dense = json.loads((notebook_dir / "state/dual_feg_dense.json").read_text())
threshold = json.loads((notebook_dir / "supplementary/b2-threshold-certificate.json").read_text())
print("Dense objective:", dense["opt_value"], "basis:", dense["basis_vectors"])
for group in dense["lambda_groups"]:
    active = [(name, value) for name, value in dense["named_dual_values"].items() if dense["constraint_metadata"][name]["group"] == group and value is not None and value > 1e-6]
    print(group, "active count:", len(active))
    print(active)
print("Dense S eigenvalues:", np.linalg.eigvalsh(np.array(dense["S_matrix"])))
print("Threshold attempt gap:", threshold["sparsity_selection"]["dense_gap"])
print("Selected structural relaxation:", b2["sparsity_selection"])
print("Dropped constraints:", len(b2["relaxed_constraints"]))
for name, value in b2["named_dual_values"].items():
    if value is not None:
        print(name, value, "near", Fraction(value).limit_denominator(1000))
'''
new=[nbf.v4.new_markdown_cell('''## Dense and relaxed proof solves
The dense $N=6$ solve was followed by a threshold relaxation dropping multipliers below $10^{-6}$. A second structural relaxation keeps terminal monotonicity to the zero and $y_0,\ldots,y_{N-2}$, plus step Lipschitz inequalities. The last step uses $(x_{N-1},x_N)$ because $x_N=y_{N-1}$; the unused duplicate evaluation is omitted. All selected components are from one fresh CLARABEL solve. Saved certificate values are revalidated below without solving again.'''),nbf.v4.new_code_cell(summary),nbf.v4.new_markdown_cell(r'''## Lambda and S verification
The numerical certificate uses residuals $r\le0$ and the identity
$$\|A(x_N)\|^2-\tau-\sum_i\lambda_i r_i+S=0.$$
Every active multiplier and all numerical LDL factors are retained. The initial residual is $\|x_0-x_\star\|^2-R^2$.

At $L=R=1$, inspection suggests terminal monotonicity weights $4/N$ to the zero and $4/[t(t-1)]$ to $y_k$, $t=N-k\ge2$; Lipschitz weights are $2/t^2$. The remainder candidate is
$$S_{\rm guess}=\left\|\frac{2}{N}(x_0-x_\star)-A(x_N)\right\|^2.$$
These are candidates supported at the selected horizon, not an arbitrary-horizon proof. No pre-existing mathematical sources were authorized. Numerical reverse LDL is kept as the exact decomposition of the selected numerical matrix.'''),nbf.v4.new_code_cell(verify),nbf.v4.new_code_cell('''pf.pprint_labeled_matrix(E, row_labels=[f"ell_{i}" for i in range(len(E))], column_labels=selected["basis_vectors"])
for group, display in selected["lambda_groups"].items():
    row_names, col_names = display["row_names"], display["col_names"]
    candidate = np.zeros((len(row_names), len(col_names)))
    for i, ri in enumerate(row_names):
        for j, cj in enumerate(col_names):
            prefix = "A monotone" if "Monotone" in group else "A Lipschitz"
            name = f"{prefix}:{ri},{cj}"
            candidate[i,j] = float(lambda_candidate(name,N))
    print("Candidate group:", group)
    pf.pprint_labeled_matrix(candidate, row_labels=row_names, column_labels=col_names)
print("Initial closed-form search:", b2["closed_form_search"])
''')]
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Dense and relaxed'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Partial-sum'))
nb.cells[start:end]=new
nbf.write(nb,path)
kdir=root/'supplementary/.runtime/kernels'
km=KernelManager(kernel_name='attempt-python',kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kdir)]))
NotebookClient(nb,timeout=120,km=km,resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb,path)
for c in nb.cells:
    if c.cell_type=='markdown':
        assert '\\(' not in c.source and '\\[' not in c.source
        assert not any(ord(x)<32 and x not in '\n\t' for x in c.source)
record={'status':'passed','fresh_kernel':True,'source_math_checks':'passed','rendered_review':'omitted by evaluation-ancillary-v1','notebook_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(root/'supplementary/b2-notebook-execution.json').write_text(json.dumps(record,indent=2))
check=root/'supplementary/dual_feg_example_lyap_checklist.md'
lines=check.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'): lines[i]='Last reviewed block: B2'
    if line.startswith('SHA-256:'): lines[i]='SHA-256: '+record['notebook_sha256']
    if line.startswith('| 7.'): lines[i]=line.split('| pending')[0]+'| verified | 8–9 | Dense, threshold and structural relaxation summaries; all group entries; preserved optimum. |'
    if line.startswith('| 8.'): lines[i]=line.split('| pending')[0]+'| verified | 10–12 | Complete numerical identity, labeled residual/candidate matrices, LDL reconstruction; analytic status candidate only. |'
    for number,cell in [(9,13),(10,14),(11,15),(12,16)]:
        if line.startswith(f'| {number}.'):
            parts=line.split('|');parts[3]=f' {cell} ';lines[i]='|'.join(parts)
check.write_text('\n'.join(lines))
print('B2 notebook executed, complete certificate checks passed.')
