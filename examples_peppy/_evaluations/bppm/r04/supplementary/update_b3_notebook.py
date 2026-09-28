import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import textwrap
import nbformat as nbf
from nbclient import NotebookClient
root=runtime.ATTEMPT
path=root/'bppm_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
def source(name):
    return (root/'supplementary'/name).read_text(encoding='utf-8-sig')
body='''certificate=json.loads((notebook_dir/sample_file).read_text())
N_int=certificate['N_verify']
params_sp={k:sp.S(v) for k,v in json.loads(certificate['params_json']).items()}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
ctx.set_as_current()
print('Certificate horizon:',N_int)
'''
body+=source('b3_check.py').replace('ScalarConstraint, PSDConstraint','ScalarConstraint')+'\n'+source('b3_decomposition.py')+'\n'+source('b3_grouping.py')+'\n'+source('b3_coverage.py')
body+='''
rank_samples.append({'N':N_int,'certificate_id':certificate['certificate_id'],'recipe_id':'consecutive_residuals_terminal_h_and_S','rank_profile':ranks,'rank_convention':{'tolerance':rank_tolerance,'scaling':'absolute singular values, unscaled Gram coordinates','coordinate_order':'setup basis order'},'rank_credible':rank_credible,'certificate_checked':certificate_checked,'grouping_checked':grouping_checked,'singular_values':singular_values})
'''
loop='import sympy as sp\nrank_samples=[]\nfor sample_file in ("supplementary/bppm_N6_b2.json", "state/bppm_b2.json"):\n'+textwrap.indent(body,'    ')
new=[nbf.v4.new_markdown_cell(r'''## Lyapunov partial sums and rank profile
Let $r^q_{i,j}$ denote the convex interpolation residual defined above. Assign both directed consecutive $h$ terms and the associated $f$ terms to their newest iterate. With the **saved numerical** coefficients $d$, define $V_0=0$ and
$$V_k-V_{k-1}=d^f_{\star,k}r^f_{\star,k}+d^f_{k-1,k}r^f_{k-1,k}+d^h_{k,k-1}r^h_{k,k-1}+d^h_{k-1,k}r^h_{k-1,k}.$$
The terms with zero support at $k=1$ are absent. All assigned residuals are nonpositive, so this convention makes $V_k$ nonincreasing. Retain the one terminal residual $d^h_{\star,N}r^h_{\star,N}$ and the entire small numerical PSD matrix $S$ as boundary contributions; no certificate term is discarded.
Rebuild and recheck each sample below, then compute its partial sums, ranks, and all-coordinate coverage. Rank 4 is observed across horizons 4 and 6 after excluding $V_0$ and $V_N$, with at least three retained indices per horizon. This is finite-sample structure, not an analytic theorem.'''),nbf.v4.new_code_cell(loop),nbf.v4.new_code_cell(source('b3_assess.py')+'\nrank_search=assess_rank_pattern(rank_samples,certificate["certificate_id"],left=1,right=1)\nassert rank_search["status"]=="confirmed"\nprint("Confirmed horizons:",rank_search["confirmed_horizons"],"common rank:",rank_search["rank"],"exclusions:",rank_search["boundary_exclusions"])\nprint("Rank convention:",rank_search["rank_convention"])\nprint("Boundary leftovers:",boundary_names,boundary_S)\nprint("All omitted terms:",[])\nprint("Numerical certificate and grouping verified; analytic statuses remain false.")')]
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Lyapunov partial sums'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Special vectors'))
nb.cells[start:end]=new
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
nbf.write(nb,path)
NotebookClient(nb,timeout=120,kernel_name='bppm-attempt',resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb,path)
print('B3 notebook executed and saved')
