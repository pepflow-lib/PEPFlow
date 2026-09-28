import importlib.util
import os
from pathlib import Path
spec = importlib.util.spec_from_file_location('runtime', Path(__file__).parent / 'helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat as nbf
from nbclient import NotebookClient
path = runtime.ROOT / 'feg_example_lyap.ipynb'
nb = nbf.read(path, as_version=4)
index = next(i for i,c in enumerate(nb.cells) if c.source.startswith('## Lyapunov partial sums'))
nb.cells[index:index] = [nbf.v4.new_markdown_cell('### Additional certificate at N=8\nThe same consecutive monotonicity and half-step Lipschitz support is used. This separate coherent sample will support the required cross-horizon comparison; N=6 remains the selected handoff.'), nbf.v4.new_code_cell('''sample8 = json.loads((notebook_dir / "supplementary/feg_certificate_N8.json").read_text())
dense8 = json.loads((notebook_dir / "supplementary/feg_dense_N8.json").read_text())
ctx8, pb8, A8, pm8, residual8, checks8 = verify_saved(sample8, dense8["opt_value"])
print("N=8 dense/relaxed objectives:", dense8["opt_value"], sample8["opt_value"])
print("N=8 complete certificate checks:", checks8)
print("Separate sample certificate ID:", sample8["certificate_id"])''')]
nbf.write(nb,path)
os.environ['JUPYTER_PATH'] = str(runtime.RUNTIME / 'jupyter')
NotebookClient(nb, timeout=120, kernel_name='feg-private', resources={'metadata': {'path':str(runtime.ROOT)}}).execute()
nbf.write(nb,path)
print('Additional certificate notebook execution passed.')
