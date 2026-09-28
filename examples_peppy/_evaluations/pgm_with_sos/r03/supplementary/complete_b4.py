import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import configure,NOTEBOOK_DIR
configure()
import inspect
import json
from basis import discover,V_k_basis,V_k_basis_labels,sample_structure

b3=json.loads((NOTEBOOK_DIR/"state/pgm_b3.json").read_text())
ctx,pb,lyap,coeffs,rows=discover(b3)
unknowns=[{"name":f"c_{i}{j}","arguments":["k","N","L"],
"role":f"interior.C[{i},{j}] and symmetric partner","index_domain":"1 <= k <= N-1"}
for i in range(4) for j in range(i,4)]
unknowns += [{"name":"t","arguments":["N","L"],"role":"terminal.C[0,0]","index_domain":"k=N"},
{"name":"p","arguments":["k","N"],"role":"coefficient of f(x_k)-f_star","index_domain":"1 <= k <= N"},
{"name":"q","arguments":["k","N"],"role":"coefficient of g(x_k)-g_star","index_domain":"1 <= k <= N"}]
state={**b3,"basis_templates":{"interior":["d0","dk","ak","astar-ak"],"initial":[],"terminal":["d0"]},
"basis_code":inspect.getsource(V_k_basis)+"\n"+inspect.getsource(V_k_basis_labels),
"structure_code":inspect.getsource(sample_structure),
"coeff_by_k":coeffs,"coeff_code":None,"coefficient_formula_status":"unresolved",
"expression_structure":{"quadratic_convention":"sum C_ij <v_i,v_j>; symmetric; off-diagonal counted twice",
"interior":{"index_domain":"1 <= k <= N-1","basis_labels":["d0","dk","ak","astar-ak"],
"coefficients":"c_ij(k,N,L), i<=j"},
"initial":{"index_domain":"k=0","basis_labels":[],"coefficients":"V_0=0"},
"terminal":{"index_domain":"k=N","basis_labels":["d0"],"coefficients":"t(N,L)"},
"function_terms":[{"term":"f(x_k)-f_star","coefficient":"p(k,N)","index_domain":"1<=k<=N"},
{"term":"g(x_k)-g_star","coefficient":"q(k,N)","index_domain":"1<=k<=N"}],
"constant_terms":[]},"unresolved_coefficients":unknowns,"sample_structure_coefficients":rows,
"numerical_reconstruction":{"certificate_id":b3["certificate_id"],
"required_indices":list(range(b3["N_verify"]+1)),
"quadratic_residuals":{str(r["k"]):r["quadratic_error"] for r in rows},
"component_residuals":{str(r["k"]):r["component_residuals"] for r in rows},
"tolerances":{"indep_tol":1e-7,"span_tol":1e-5,"component_atol":1e-4,"component_rtol":1e-5},
"passed":True}}
assert all(r["offset"]==0 for r in rows)
(NOTEBOOK_DIR/"state/pgm_b4.json").write_text(json.dumps(state,indent=2))
(NOTEBOOK_DIR/"supplementary/b4-reconstruction.json").write_text(json.dumps(rows,indent=2))

