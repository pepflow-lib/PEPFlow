import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from owned_runtime import configure, ROOT, APPROVED
configure()
import json
import numpy as np
import sympy as sp
import pepflow as pf
from pgm_setup import get_pep_setup
from solve_runtime import solve_primal

notebook_dir=ROOT
repo_root=APPROVED
n=6
ctx,pb,obj=get_pep_setup(n,{})
result,meta=solve_primal(ctx,pb,{'L':sp.Integer(1),'R':sp.Integer(1)})
duals={name:np.asarray(c.dual_value).tolist() for name,c in result.dual_var_manager.named_constraints.items()}
dense_data={'N':n,'opt_value':result.opt_value,'solver':meta,'named_duals':duals,
    'S_matrix':result.get_gram_dual_matrix().matrix.tolist(),'basis_vectors':[str(v) for v in ctx.basis_vectors()]}
(ROOT/'supplementary/b2-n06-dense.json').write_text(json.dumps(dense_data,indent=2))
print('N6 dense',result.opt_value,meta,flush=True)
source=(ROOT/'supplementary/b2_cells.py').read_text(encoding='utf-8-sig')
source=source.replace("N_int = b1['N_verify']",'N_int = 6')
source=source.replace("dense_data = json.loads((notebook_dir / 'state' / 'pgm_dense.json').read_text())", "dense_data = json.loads((notebook_dir / 'supplementary' / 'b2-n06-dense.json').read_text())")
source=source.replace("for filename in ('pgm_relaxed.json','pgm_b2.json'):","for filename in ('b2-n06-certificate.json',):")
source=source.replace("(notebook_dir/'state'/filename)","(notebook_dir/'supplementary'/filename)")
source=source.replace('    pf.pprint_labeled_matrix(pf.MatrixWithNames(matrix, labels, labels))', '    print(str(owner), "candidate matrix checked")')
source=source.replace('pf.pprint_labeled_matrix(pf.MatrixWithNames(S_candidate, S_sol.row_names, S_sol.col_names))','print("Candidate S checked")')
source=source.replace('pf.pprint_labeled_matrix(pf.MatrixWithNames(S_reconstructed-S_array, S_sol.row_names, S_sol.col_names))','print("Reconstruction checked")')
source=source.replace('pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(checked.inner_prod_coords,dtype=float), S_sol.row_names,S_sol.col_names))','print("Gram identity checked")')
(ROOT/'supplementary/b2-n06-executed-source.py').write_text(source,encoding='utf-8')
exec(compile(source,'b2-n06-executed-source.py','exec'),globals())
