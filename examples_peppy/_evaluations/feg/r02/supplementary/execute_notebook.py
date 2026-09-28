import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import os
import nbformat
from nbclient import NotebookClient
root=Path(__file__).resolve().parents[1]
path=root/'feg_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
os.environ['JUPYTER_PATH']=str(root/'supplementary/.runtime/jupyter')
NotebookClient(nb,timeout=120,kernel_name='feg-owned',resources={'metadata':{'path':str(root)}}).execute()
nbformat.write(nb,path)
print('Fresh execution passed:',len(nb.cells),'cells')
