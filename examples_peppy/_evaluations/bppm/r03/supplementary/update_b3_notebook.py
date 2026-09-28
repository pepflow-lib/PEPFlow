import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat as nb
from nbclient import NotebookClient
import os
root=runtime.ROOT
path=root/'bppm_example_lyap.ipynb'
book=nb.read(path,as_version=4)
md,code=nb.v4.new_markdown_cell,nb.v4.new_code_cell
cells=[md(r'''## Partial-sum Lyapunov construction (Block 3)
Let $V_0=0$. At step $i=1,\ldots,N$, accumulate the saved multipliers on $Q^f_{\star,i}$, $Q^h_{i,i-1}$, and for $i\geq2$ on $Q^f_{i-1,i}$ and $Q^h_{i-1,i}$. Thus
$$V_i-V_{i-1}=d^f_{\star,i}Q^f_{\star,i}+d^h_{i,i-1}Q^h_{i,i-1}+\mathbf1_{i\geq2}\bigl(d^f_{i-1,i}Q^f_{i-1,i}+d^h_{i-1,i}Q^h_{i-1,i}\bigr)\leq0.$$
The single terminal inequality $d^h_{\star,N}Q^h_{\star,N}$ and the entire numerical PSD remainder $S$ are boundary terms. Nothing is omitted. The normalization inequality is reserved for the initial bound.
The observed Gram rank is 4 at every nonzero index for horizons 4 and 6. Fixed exclusions $(1,1)$ leave at least three indices at each horizon. The rank tolerance is $10^{-4}$ with no matrix rescaling; all singular values lie outside the ambiguity band $[10^{-5},10^{-3}]$. This is finite-sample evidence, not a theorem.'''),
code('sys.path.insert(0,str(notebook_dir / "supplementary/helpers"))\nREPO_ROOT = repo_root\ncertificate = json.loads((notebook_dir / "state/bppm_b3.json").read_text())\nN_int = certificate["N_verify"]\nparams_sp = json.loads(certificate["params_json"])\nctx,pb,obj = get_pep_setup(N_int,params_sp)\npb.set_relaxed_constraints(certificate["relaxed_constraints"])'),
code((root/'supplementary/b3_certificate_check.py').read_text(encoding='utf-8-sig')),
code((root/'supplementary/b3_decomposition.py').read_text(encoding='utf-8-sig')),
code((root/'supplementary/b3_grouping.py').read_text(encoding='utf-8-sig')),
code('rank_evidence = json.loads((notebook_dir / "supplementary/rank_search.json").read_text())\nfor sample in rank_evidence["samples"]:\n    print("N",sample["N"],"retained ranks",sample["rank_profile"][1:-1],"coverage",sample["coverage_errors"])\n    assert sample["certificate_checked"] and sample["grouping_checked"] and sample["rank_credible"]\n    assert len(sample["rank_profile"][1:-1])>=3\n    assert set(sample["rank_profile"][1:-1])=={4}\nprint("Common rank 4 confirmed at N=4,6; exclusions (1,1), absolute tolerance 1e-4, no rescaling.")')]
book.cells[18:24]=cells
os.environ['JUPYTER_PATH']=str(root/'supplementary/.runtime')
NotebookClient(book,timeout=120,kernel_name='bppm-owned',resources={'metadata':{'path':str(root)}}).execute()
nb.write(book,path)
print('B3 notebook updated and executed.')

