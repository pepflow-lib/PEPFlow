"""Run visible B4 cells and save the numerical structure."""
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[key]="1"
sys.path[:0]=[str(ROOT/"supplementary"/"approved"),str(ROOT),str(ROOT/"supplementary"/"helpers")]
import nbformat as nbf  # noqa: E402
import numpy as np  # noqa: E402
import pepflow as pf  # noqa: E402
import sympy as sp  # noqa: E402
from partial_sums import build_partial_sums, check_certificate  # noqa: E402

source=(ROOT/"supplementary"/"b4_cells.py").read_text()
namespace: dict[str, Any]=dict(json=json,np=np,pf=pf,sp=sp,notebook_dir=ROOT,check_certificate=check_certificate,build_partial_sums=build_partial_sums)
exec(compile(source,"b4_cells.py","exec"),namespace)
b3=namespace["b3"]
parts={chunk.split('\n',1)[0]:chunk.split('\n',1)[1] for chunk in source.split('# %% ')[1:]}
basis_code=parts["Basis"].split('for k in range(N_int+1):',1)[0]
function_data=namespace["function_coefficients"]
gauge_data=namespace["gauge_coefficients"]
structure_code='function_coefficients = '+repr(function_data)+'\ngauge_coefficients = '+repr(gauge_data)+'\n'+parts["Structure"].split('component_residuals =',1)[0]
unknowns=[]
interior_coefficients={}
initial_coefficients={}
for size,prefix,domain,destination in ((4,"c","2 <= k <= N",interior_coefficients),(3,"d","k=1",initial_coefficients)):
    for i in range(size):
        for j in range(i,size):
            name=f"{prefix}_{i}{j}"
            destination[f"{i},{j}"]=name+"(k,N,L)"
            unknowns.append(dict(name=name,arguments=["k","N","L"],role=f"{prefix}.C[{i},{j}] symmetric",index_domain=domain))
unknowns.extend([dict(name="a",arguments=["k","j","N","L"],role="coefficient of f(x_j)-f_star",index_domain="0 <= j <= k <= N"),dict(name="b",arguments=["k","N","L"],role="gauge coefficient of f_star; numerically zero",index_domain="0 <= k <= N")])
structure: dict[str, Any]=dict(quadratic_convention="sum_i,j C_ij <v_i,v_j>; symmetric C, off-diagonal entries counted twice",interior=dict(index_domain="2 <= k <= N, exclusions left=2 right=0",basis_labels=["x_0-x_star","z_k-x_star","x_k-x_star","g_k"],coefficients=interior_coefficients),initial=dict(index_domain="k=0,1",cases={"0":{"basis_labels":[],"quadratic":0},"1":{"basis_labels":["x_0-x_star","z_1-x_star","g_1"],"coefficients":initial_coefficients}}),terminal=dict(index_domain="empty; k=N follows interior when N>=2, k=1 case when N=1"),function_terms=[dict(expression="sum_{j=0}^k a(k,j,N,L)*(f(x_j)-f_star) + b(k,N,L)*f_star",index_domain="0<=k<=N",numerical_observation="Earlier j<k coefficients and gauge b are near zero; terminal gap coefficient remains nonzero")],constant_terms=[])
state={**b3,"basis_templates":structure["interior"]["basis_labels"],"basis_code":basis_code,"structure_code":structure_code,"coeff_by_k":{str(k):C.tolist() for k,C in namespace["coeff_by_k"].items()},"coeff_code":None,"coefficient_formula_status":"unresolved","expression_structure":structure,"unresolved_coefficients":unknowns,"numerical_reconstruction":dict(certificate_id=b3["certificate_id"],required_indices=list(range(b3["N"]+1)),quadratic_residuals=namespace["coefficient_residuals"],component_residuals=namespace["component_residuals"],tolerances=dict(indep_tol=1e-7,span_tol=1e-5,component_atol=1e-4,component_rtol=1e-5),passed=True)}
(ROOT/"state"/"ogm_b4.json").write_text(json.dumps(state,indent=2))
path=ROOT/"ogm_example_lyap.ipynb"
nb=nbf.read(path,as_version=4)
start=next(i for i,cell in enumerate(nb.cells) if cell.cell_type=='markdown' and cell.source.startswith('## Identify the vectors composing'))
nb.cells=nb.cells[:start]
nb.cells.extend([
nbf.v4.new_markdown_cell("## Identify the vectors composing the Lyapunov function\nThe selected partial sums are rebuilt from the same horizon-4 certificate. The retained range is k=2 through N; k=0 and k=1 remain explicit reconstruction obligations."),nbf.v4.new_code_cell(parts["Rebuild"]),
nbf.v4.new_markdown_cell("### Candidate-vector scan\nCandidates include iterate and auxiliary gaps to the minimizer, gradients, consecutive differences, auxiliary-minus-primary differences, and basis vectors. Zero vectors and coordinate duplicates are removed."),nbf.v4.new_code_cell(parts["Candidates"]),
nbf.v4.new_markdown_cell("### Selected basis pattern"),nbf.v4.new_code_cell(parts["Search"]),
nbf.v4.new_markdown_cell(r"""The search sometimes selects future auxiliary iterates. We use the equally valid current-iterate basis to make the recurrence local:
$$[x_0-x_\star,\ z_k-x_\star,\ x_k-x_\star,\ g_k],\qquad 2\leq k\leq N.$$
At $k=1$ use $[x_0-x_\star,z_1-x_\star,g_1]$ because the current iterate gap is dependent. At $k=0$ the quadratic part is zero. The adopted basis is checked independently below.
"""),nbf.v4.new_code_cell(parts["Basis"]),
nbf.v4.new_markdown_cell("### Coefficient matrices\nMatrices use the displayed basis order and count symmetric off-diagonal entries twice. Every function coordinate is retained as a gap coefficient plus the residual absolute function-value coefficient; scalar offsets are checked to vanish."),nbf.v4.new_code_cell(parts["Coefficients"]),nbf.v4.new_code_cell(parts["Structure"]),
nbf.v4.new_markdown_cell(r"""### Block 4 conclusion
The numerical expression is
$$V_k=\sum_{i,j}c_{ij}(k,N,L)\langle v_i,v_j\rangle+\sum_{j=0}^k a(k,j,N,L)(f(x_j)-f_\star)+b(k,N,L)f_\star.$$
The matrix is symmetric. The initial $k=1$ case has its own three-vector coefficient functions $d_{ij}(1,N,L)$; $V_0=0$. The absolute-function coefficient and earlier function gaps are numerically negligible, but remain in the checked numerical representation. No coefficient formula has yet been asserted universally. Block 5 must derive them and establish the exact step, base, and terminal identities. Every required numerical index has passed full reconstruction.

## Closed-form Lyapunov function and symbolic identities (pending Block 5)
""")])
nbf.write(nb,path)
checklist=ROOT/"supplementary"/"ogm_example_lyap_checklist.md"
lines=checklist.read_text().replace("Last reviewed block: B3","Last reviewed block: B4").splitlines()
for i,line in enumerate(lines):
    if line.startswith("| 10 |"):
        fields=line.split('|')
        fields[3]=' verified '
        fields[4]=' 21-32 '
        fields[5]=' Candidate scan, actual sparse search, adopted basis independence, all-index coefficient and full-coordinate reconstruction executed. '
        lines[i]='|'.join(fields)
    if line.startswith("| 11 |"):
        fields=line.split('|')
        fields[4]=' 29-32 '
        fields[5]=' Numerical coefficients extracted; closed form remains a Block 5 obligation. '
        lines[i]='|'.join(fields)
checklist.write_text('\n'.join(lines))
print("B4 numerical reconstruction complete.")

