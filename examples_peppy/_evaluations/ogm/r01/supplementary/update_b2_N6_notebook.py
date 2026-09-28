import sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'supplementary/helpers'))
import runtime
import os
import nbformat
from nbclient import NotebookClient
path=root/'ogm_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
nb.cells[15].source += '''
# Independent confirmation sample, acquired on the B2 revisit.
with (notebook_dir / "supplementary/ogm_b2_N6.json").open() as stream:
    b2_N6 = json.load(stream)
assert certificate_digest(b2_N6) == b2_N6["certificate_id"]
N6_replay = verify_certificate(b2_N6)
print("N=6 independent certificate checks:", N6_replay[-1])
print("Selected main certificate remains N=4.")
'''
nbformat.write(nb,path)
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
NotebookClient(nb,timeout=120,kernel_name='ogm-attempt',resources={'metadata':{'path':str(root)}}).execute()
nbformat.write(nb,path)
print('Independent N=6 certificate replayed in notebook.')
