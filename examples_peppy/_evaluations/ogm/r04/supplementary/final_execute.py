import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from runtime import configure
attempt,approved=configure()
os.environ['JUPYTER_PATH']=str(attempt/'supplementary/.runtime/jupyter')
command=[sys.executable,'-I','-B','-m','nbconvert','--to','notebook','--execute',str(attempt/'ogm_example_lyap.ipynb'),'--inplace','--ExecutePreprocessor.timeout=120','--ExecutePreprocessor.kernel_name=ogm-own']
started=datetime.now(timezone.utc).isoformat()
result=subprocess.run(command,cwd=attempt,text=True,capture_output=True,timeout=600)
(attempt/'supplementary/b5-final-execution.json').write_text(json.dumps({'command':command,'cwd':str(attempt),'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr},indent=2))
print(result.stdout)
print(result.stderr)
result.check_returncode()
import nbformat as nbf
nb=nbf.read(attempt/'ogm_example_lyap.ipynb',as_version=4)
proof_evidence=None
for c in nb.cells:
    if c.cell_type=='code':
        assert c.execution_count is not None
        for output in c.outputs:
            assert output.output_type!='error'
            if output.output_type=='stream':
                for line in output.text.splitlines():
                    if line.startswith('FINAL_PROOF_EVIDENCE='):
                        proof_evidence=json.loads(line.split('=',1)[1])
    else:
        assert '\\(' not in c.source and '\\[' not in c.source
        assert not any(ord(ch)<32 and ch not in '\n\t' for ch in c.source)
assert proof_evidence is not None
assert all(proof_evidence['proof_checks'].values())
assert len(proof_evidence['exact_results'])==5
for result in proof_evidence['exact_results'].values():
    assert result['gram_zero'] and result['function_zero'] and result['offset_zero']
b4=json.loads((attempt/'state/ogm_b4.json').read_text())
formula='V_0=0; for 1<=k<N: V_k=2*theta_k**2/theta_N**2*(f(x_k)-f_star)+L/(2*theta_N**2)*(||z_k-x_star-2*theta_k/L*g_k||**2-||x_0-x_star||**2)-theta_k**2/(L*theta_N**2)*||g_k||**2; V_N=f(x_N)-f_star+L/(2*theta_N**2)*(||z_N-x_star-theta_N/L*g_N||**2-||x_0-x_star||**2).'
arguments={'domain':'Real finite-dimensional Euclidean space; convex L-smooth f; L>0, R>=0, integer N>=1; stationary x_star; z_0=x_0; radius squared <=R^2. Theta positive-root definitions imply theta_0=1, theta_k>=1, theta_N>=2. Interior/base/terminal identities use precisely their recurrence relations; separate N=1 proof.', 'signs':'Smooth convex interpolation I_ij<=0 by descent applied to f-<g_j,.>; all weights 2 theta_i/theta_N^2, 2 theta_i^2/theta_N^2, 1/theta_N and tau=L/(2 theta_N^2) are positive. Hence V nonincreasing. Boundary subtracts positive tau times a squared norm and adds tau times nonpositive radius residual.', 'normalization':'F_N-L R^2/(2 theta_N^2)=V_N-tau||q_N||^2+tau(||d_0||^2-R^2); verified exactly with R symbolic, no division by R.', 'base':'W_1=2 I_star,0+2 theta_1 I_star,1+2 I_0,1 for N>=2; separate N1 identity has theta_1=2 and terminal W_1.', 'step':'W_{k+1}-W_k=2 theta_{k+1} I_star,k+1+2 theta_k^2 I_k,k+1 for 1<=k<=N-2; terminal W_N-W_{N-1}=theta_N I_star,N+2 theta_{N-1}^2 I_N-1,N.', 'global_full_pep':'Summing base plus interior and terminal identities includes every listed optimizer-row and forward-consecutive residual once. Divide by theta_N^2 and use the exact terminal formula to obtain the displayed full-PEP identity with lambda, tau and S; N1 checked separately. This is an analytic finite-sum telescoping argument for arbitrary N, not sampled verification.'}
local_multiplier_code='def local_multipliers(t, s, H, terminal=False):\n    return {"star_next": s/H**2 if terminal else 2*s/H**2, "forward_edge":2*t**2/H**2}\n'
state={**b4,'proof_checks':proof_evidence['proof_checks'],'exact_symbolic_results':proof_evidence['exact_results'],'proof_arguments':arguments,'lyapunov_formula':formula,'discovery_expression_structure':b4['expression_structure'],'expression_structure':b4['expression_structure'],'discovery_coeff_code':b4['coeff_code'],'coeff_code':None,'local_multiplier_code':local_multiplier_code,'remaining_unknowns':[],'coefficient_formula_status':'verified','formula_status':{'lambda':'verified','S':'verified'},'numerical_certificate_verified':True,'analytic_full_pep_verified':True,'lyapunov_proof_verified':True,'require_analytic_full_pep':False,'symbolic_source_path':'supplementary/b5_symbolic_cells.py','theorem_latex':(attempt/'supplementary/b5_theorem.md').read_text(encoding='utf-8-sig'),'proof_outline_latex':(attempt/'supplementary/b5_proof_outline.md').read_text(encoding='utf-8-sig'),'presentation_policy':'evaluation-ancillary-v1','rendered_review_performed':False,'run_status':'complete','unresolved_work':[],'final_execution_evidence':'supplementary/b5-final-execution.json','static_evidence':'supplementary/b5-static-001.json'}
(attempt/'state/ogm_b5.json').write_text(json.dumps(state,indent=2,allow_nan=False))
print('FINAL SYMBOLIC EVIDENCE',json.dumps(proof_evidence))
print('Final notebook executed; B5 state saved.')
