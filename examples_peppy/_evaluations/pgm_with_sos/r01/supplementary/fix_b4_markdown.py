import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat as nb
import hashlib
import re
root=runtime.ATTEMPT
path=root/'pgm_example_lyap.ipynb'
book=nb.read(path,as_version=4)
for cell in book.cells:
    if cell.cell_type=='markdown':
        cell.source=cell.source.replace('\r',r'\r')
        assert not any(s in cell.source for s in ('\\(', '\\)', '\\[', '\\]', '\x0c', '\r'))
nb.write(book,path)
p=root/'supplementary/update_b4_notebook.py'
p.write_text(p.read_text().replace("nb.v4.new_markdown_cell('''","nb.v4.new_markdown_cell(r'''"))
p=root/'supplementary/pgm_example_lyap_checklist.md'
s=p.read_text()
s=re.sub(r'Last reviewed block:.*','Last reviewed block: B4',s)
s=re.sub(r'SHA-256: [a-f0-9]+','SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest(),s)
s=s.replace('| pending | 15 | B3 slack allocation recovered; B4 search and all-index reconstruction must be rerun. |','| verified | 15-25 | Executed candidate filtering, sparse search, consistent adopted basis and independence/full-expression reconstruction for every index. |')
s=s.replace('| pending | 16 | Due B4/B5. |','| pending | 24-26 | B4 numerical coefficient extraction and expression structure verified; closed-form functions due in B5. |')
s=s.replace('| pending | 16 | Due B5. |','| pending | 27 | Due B5. |')
p.write_text(s)
print('Markdown carriage-return escape repaired; source checks passed; executed mathematical outputs preserved.')
