import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import nbformat as nb
root=runtime.ATTEMPT
p=root/'supplementary/b3_decomposition.py'
s=p.read_text().replace('matrix[i,l]','matrix[i,col_idx]').replace('basis[l]','basis[col_idx]').replace('for i,l in','for i,col_idx in')
p.write_text(s)
p=root/'state/pgm_b3.json'
b3=json.loads(p.read_text());b3['decomposition_code']=s;p.write_text(json.dumps(b3,indent=2))
p=root/'pgm_example_lyap.ipynb'
book=nb.read(p,as_version=4)
book.cells[14].source=book.cells[14].source.replace('matrix[i,l]','matrix[i,col_idx]').replace('basis[l]','basis[col_idx]').replace('for i,l in','for i,col_idx in')
nb.write(book,p)
