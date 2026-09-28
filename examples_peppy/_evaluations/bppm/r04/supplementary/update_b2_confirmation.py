import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import nbformat as nbf
from nbclient import NotebookClient
root=runtime.ATTEMPT
path=root/'bppm_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
index=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Lyapunov partial sums'))
nb.cells[index:index]=[nbf.v4.new_markdown_cell('### Additional coherent certificate for rank confirmation\nB3 requested a distinct horizon. B2 acquired the $N=6$ dense and consecutive-pair samples with the same solver settings and formula recipe. This cell independently checks the supplementary certificate; the selected $N=4$ state remains unchanged.'),nbf.v4.new_code_cell('confirmation = json.loads((notebook_dir/"supplementary/bppm_N6_b2.json").read_text())\ndense6 = json.loads((notebook_dir/"supplementary/bppm_N6_dense.json").read_text())\nparams6 = json.loads(confirmation["params_json"])\nctx6, pb6, obj6 = get_pep_setup(confirmation["N_verify"], params6)\npb6.set_relaxed_constraints(confirmation["relaxed_constraints"])\nfor relative, expected in confirmation["certificate_provenance"]["source_hashes"].items():\n    assert hashlib.sha256((notebook_dir/relative).read_bytes()).hexdigest() == expected\nchecked6 = verify_certificate(ctx6, pb6, confirmation, dense6["opt_value"])\nprint("Additional horizon:",confirmation["N_verify"], "dense bound:",dense6["opt_value"], "selected bound:",confirmation["opt_value"])\nprint("Candidate checks:",confirmation["closed_form_search"]["candidate_lambda_max_error"],confirmation["closed_form_search"]["candidate_S_max_error"])\nctx.set_as_current()')]
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
nbf.write(nb,path)
NotebookClient(nb,timeout=120,kernel_name='bppm-attempt',resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb,path)
print('B2 confirmation notebook executed')
