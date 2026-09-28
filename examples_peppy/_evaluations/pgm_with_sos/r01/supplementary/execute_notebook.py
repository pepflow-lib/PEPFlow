import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import re
import hashlib
import nbformat as nb
from nbclient import NotebookClient
root=runtime.ATTEMPT
path=root/'pgm_example_lyap.ipynb'
book=nb.read(path,as_version=4)
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
NotebookClient(book,timeout=180,kernel_name='pgm-attempt',resources={'metadata':{'path':str(root)}}).execute()
nb.write(book,path)
for cell in book.cells:
    if cell.cell_type=='markdown':
        assert not any(s in cell.source for s in ('\\(', '\\)', '\\[', '\\]', '\x0c', '\r'))
p=root/'supplementary/pgm_example_lyap_checklist.md'
s=re.sub(r'SHA-256: [a-f0-9]+','SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest(),p.read_text())
p.write_text(s)
print('Fresh notebook execution and Markdown source checks passed.')
