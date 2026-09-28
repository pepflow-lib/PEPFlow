import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import nbformat
from nbclient import NotebookClient
root=runtime.ATTEMPT
path=root/'dual_feg_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
i=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Partial-sum'))
nb.cells[i:i]=[nbformat.v4.new_markdown_cell('### Additional coherent certificate at N=8\nB3 requested an independent horizon-specific certificate using the same sparse-support recipe. Both dense and sparse solves returned `optimal`; the selected main handoff remains N=6. The complete N=8 sample is retained in supplementary/n8-dual_feg_b2.json. The identity logic is the same full-coordinate check shown above; it is replayed below alongside the saved-factor reconstruction.'),nbformat.v4.new_code_cell('''from certificate import verify

sample8 = json.loads((notebook_dir / "supplementary/n8-dual_feg_b2.json").read_text())
dense8 = json.loads((notebook_dir / "supplementary/b2-n8-dense.json").read_text())
checks8, passed8 = verify(sample8, dense8["opt_value"])
D8 = np.asarray(sample8["numerical_decomposition"]["D"])
E8 = np.asarray(sample8["numerical_decomposition"]["ell_coords"])
S8 = np.asarray(sample8["S_matrix"])
assert passed8
assert np.allclose(E8.T @ D8 @ E8, S8, atol=1e-4, rtol=1e-5)
print("N=8 certificate rechecked:", passed8)
print("N=8 full-coordinate residuals:", checks8)
print("N=8 factor reconstruction max error:", np.max(np.abs(E8.T @ D8 @ E8-S8)))
print("Analytic full-PEP and Lyapunov proofs remain unverified.")
''')]
nbformat.write(nb,path)
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
NotebookClient(nb,timeout=120,kernel_name='dual-feg-attempt',resources={'metadata':{'path':str(root)}}).execute()
nbformat.write(nb,path)
print('Additional N8 certificate notebook replay passed')
