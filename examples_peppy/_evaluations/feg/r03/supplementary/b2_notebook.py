import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import hashlib
import nbformat as nbf
from nbclient import NotebookClient
ROOT=runtime.ROOT
path=ROOT/'feg_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
state=json.loads((ROOT/'state/feg_b2.json').read_text())
md=nbf.v4.new_markdown_cell
code=nbf.v4.new_code_cell
start=next(i for i,c in enumerate(nb.cells) if c.source.startswith('## Dense and relaxed'))
end=next(i for i,c in enumerate(nb.cells) if c.source.startswith('## Partial-sum'))
cells=[md('## Dense and relaxed proof solves\nThe dense solve and a fresh sparse solve use CLARABEL defaults at N=4. Saved data below retain the complete constraint inventory, dual multipliers and Gram remainder from a single selected solve. A threshold of 1e-6 selected constraints to drop; the sparse optimum was re-solved and checked. No rounding was applied to the certificate.'),code('''import hashlib
from pepflow.utils import Comparator
b2 = json.loads((notebook_dir / "state/feg_b2.json").read_text())
dense = json.loads((notebook_dir / "state/feg_dense.json").read_text())
print("Dense optimum:", dense["opt_value"])
print("Selected sparse optimum:", b2["opt_value"])
print("Basis:", b2["basis_vectors"])
print("Dropped constraints:", len(b2["relaxed_constraints"]))
for group in dense["lambda_groups"]:
    count = sum(abs(v) > 1e-6 for name,v in dense["named_dual_values"].items() if dense["constraint_metadata"][name]["group"] == group)
    print(group, "active dense entries:", count)
assert abs(dense["opt_value"]-b2["opt_value"]) < 1e-5
assert abs(b2["opt_value"]-4/b2["N"]**2) < 1e-5
print("Preserved optimum and conjectured normalization confirmed.")'''),md('### Selected multipliers\nEvery retained interpolation multiplier is displayed below. Initial-constraint normalization is retained separately.'),code('''for name,value in b2["named_dual_values"].items():
    if value is not None:
        print(name, value)
print("Numerical rank of S at absolute tolerance 1e-4:", np.linalg.matrix_rank(np.array(b2["S_matrix"]), tol=1e-4))'''),md(r'''## Lambda and S verification
The initial formula search suggests the following candidates, with $g_k=A(x_k)$: monotonicity multipliers $4Lk(k+1)/N^2$ for $(x_k,x_{k+1})$, $1\le k<N$, and $4L/N$ for $(x_N,x_\star)$; Lipschitz multipliers $2(k+1)^2/N^2$ for $(x_{k+1/2},x_{k+1})$, $0\le k<N$. The initial multiplier is $4L^2/N^2$.
The candidate Gram remainder is
$$S_{\rm guess}=\left\|\frac{2L}{N}(x_0-x_\star)-g_N\right\|^2.$$
These formulas have only a finite-sample check here. The all-horizon identity remains unresolved. Numerical verification uses the full selected remainder and all its eigenfactors, including small eigenvalues.'''),code(state['lamb_code']+'\n'+state['S_code']),code('''N_cert = b2["N_verify"]
params_cert = json.loads(b2["params_json"])
ctx, pb, op = get_pep_setup(N_cert, params_cert)
ctx.set_as_current()
pm = pf.ExpressionManager(ctx, resolve_parameters=params_cert)
entries = [(c, "initial", None, None) for c in pb.init_conditions]
groups = op.get_interpolation_constraints_by_group(ctx)
assert not groups.psd_dict
entries += [(c, "interpolation", str(op), group) for group, constraints in groups.sc_dict.items() for c in constraints]
assert {c.name for c,*_ in entries} == set(b2["constraint_metadata"]) == set(b2["named_dual_values"])
assert [str(v) for v in ctx.basis_vectors()] == b2["basis_vectors"]
assert [str(v) for v in ctx.basis_scalars()] == b2["basis_scalars"]
for c,origin,owner,group in entries:
    meta = b2["constraint_metadata"][c.name]
    assert (meta["origin"],meta["owner"],meta["group"],meta["comparator"]) == (origin,owner,group,c.cmp.value)
    assert meta["relaxed"] == (c.name in b2["relaxed_constraints"])
for relative,digest in b2["certificate_provenance"]["source_hashes"].items():
    assert hashlib.sha256((notebook_dir/relative).read_bytes()).hexdigest() == digest
certificate_keys = ('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')
assert hashlib.sha256(json.dumps({key:b2[key] for key in certificate_keys},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest() == b2["certificate_id"]
print("Certificate inventory, source hashes, coordinates and identity hash confirmed.")'''),code('''basis = ctx.basis_vectors()
S_array = np.array(b2["S_matrix"])
D = np.array(b2["numerical_decomposition"]["D"])
E = np.array(b2["numerical_decomposition"]["ell_coords"])
ell = [sum((float(c)*v for c,v in zip(row,basis)),pf.Vector.zero()) for row in E]
S_numeric = sum((float(D[i,j])*ell[i]*ell[j] for i,j in np.ndindex(D.shape)),pf.Scalar.zero())
assert np.allclose(E.T@D@E,S_array,atol=1e-4,rtol=1e-5)
assert np.linalg.eigvalsh(S_array).min() >= -1e-6
print("Full direct eigenfactor weights:", np.diag(D))
print("Reconstruction maximum residual:", np.max(np.abs(E.T@D@E-S_array)))
guess = pm.eval_scalar(S_candidate(ctx,op,N_cert,params_cert["L"]))
S_guess_matrix = np.asarray(guess.inner_prod_coords,dtype=float)
assert np.max(np.abs(S_guess_matrix-S_array)) <= 1e-4
assert np.max(np.abs(np.asarray(guess.func_coords,dtype=float)),initial=0) == 0
assert float(guess.offset) == 0
pf.pprint_labeled_matrix(pf.MatrixWithNames(S_guess_matrix,b2["basis_vectors"],b2["basis_vectors"]))
lambda_error = max(abs(float(lambda_candidate(name,N_cert,params_cert["L"]))-float(value or 0)) for name,value in b2["named_dual_values"].items())
assert lambda_error <= 1e-4
print("Candidate lambda discrepancy:",lambda_error)
print("Candidate S discrepancy:",np.max(np.abs(S_guess_matrix-S_array)))'''),md(r'''### Complete fixed-sample certificate identity
Each inequality is normalized to a residual $r_c\le0$. Check all coordinates of
$$\|A(x_N)\|^2-\mathrm{opt}-\sum_c\lambda_c r_c+S=0.$$
Nonnegative multipliers and $S\ge0$ give the bound at this numerical sample, within the recorded tolerances. This is numerical consistency, not a symbolic proof for every horizon.'''),code('''weighted = pf.Scalar.zero()
for c,*_ in entries:
    value = b2["named_dual_values"][c.name]
    if c.name in b2["relaxed_constraints"]:
        assert value is None
        continue
    assert value is not None and np.isfinite(value)
    assert value >= -1e-6
    residual = c.lhs-c.rhs
    if c.cmp in (Comparator.GE,Comparator.SEQ):
        residual = -residual
    weighted += value*(pf.Scalar.zero()+residual)
check = pm.eval_scalar(pb.performance_metric-b2["opt_value"]-weighted+S_numeric)
check_gram = np.asarray(check.inner_prod_coords,dtype=float)
check_func = np.asarray(check.func_coords,dtype=float)
residuals = {"Gram": float(np.max(np.abs(check_gram),initial=0)),"function":float(np.max(np.abs(check_func),initial=0)),"constant":abs(float(check.offset))}
assert all(value<=1e-5 for value in residuals.values())
pf.pprint_labeled_matrix(pf.MatrixWithNames(check_gram,b2["basis_vectors"],b2["basis_vectors"]))
print("Identity residuals:",residuals)
print("Numerical certificate verified; analytic full-PEP and Lyapunov proof remain unproved.")
print("Initial closed-form search:",b2["closed_form_search"])
candidate_weighted = pf.Scalar.zero()
for c,*_ in entries:
    residual = c.lhs-c.rhs
    if c.cmp in (Comparator.GE,Comparator.SEQ):
        residual = -residual
    candidate_weighted += lambda_candidate(c.name,N_cert,params_cert["L"])*(pf.Scalar.zero()+residual)
candidate_check = pm.eval_scalar(pb.performance_metric-4*params_cert["L"]**2*params_cert["R"]**2/N_cert**2-candidate_weighted+S_candidate(ctx,op,N_cert,params_cert["L"]))
print("Candidate joint sample residual:",np.max(np.abs(np.asarray(candidate_check.inner_prod_coords,dtype=float)),initial=0))''')]
nb.cells[start:end]=cells
nbf.write(nb,path)
NotebookClient(nb,timeout=120,kernel_name='feg-private',resources={'metadata':{'path':str(ROOT)}}).execute()
nbf.write(nb,path)
for cell in nb.cells:
    if cell.cell_type=='markdown':
        assert '\\(' not in cell.source and '\\[' not in cell.source
        assert all(ord(ch)>=32 or ch in '\n\t' for ch in cell.source)
    assert all(out.output_type!='error' for out in cell.get('outputs',[]))
checklist=ROOT/'supplementary/feg_example_lyap_checklist.md'
lines=checklist.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'): lines[i]='Last reviewed block: B2'
    if line.startswith('SHA-256:'): lines[i]='SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()
    if line.startswith('| 7 |'): lines[i]=f'| 7 | dense and relaxed proof solves | verified | {start}-{start+3} | Coherent saved solves, all active groups and retained multipliers; preserved-optimum check executed. |'
    if line.startswith('| 8 |'): lines[i]=f'| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | {start+4}-{start+9} | Complete inventory, hash, coordinate, sign, reconstruction and Gram/function/constant checks executed; candidate comparisons and unresolved all-horizon status explicit. |'
    for item,heading in [(9,'## Partial-sum'),(10,'## Identify'),(11,'## Coefficient'),(12,'## Symbolic')]:
        if line.startswith(f'| {item} |'):
            parts=line.split('|'); parts[4]=' '+str(next(j for j,c in enumerate(nb.cells) if c.source.startswith(heading)))+' '; lines[i]='|'.join(parts)
checklist.write_text('\n'.join(lines)+'\n')
print('B2 notebook executed:',len(nb.cells),'cells')
