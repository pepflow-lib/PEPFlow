import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat as nb
root=runtime.ATTEMPT
path=root/'pgm_example_lyap.ipynb'
book=nb.read(path,as_version=4)
book.cells=book.cells[:13]+[nb.v4.new_markdown_cell('## Lyapunov partial sums and ranks\nThe N=4 observation is preserved in supplementary/rank_N4.json. The selected N=6 certificate now requires B3 reconstruction and comparison; that work has not started.')]+book.cells[-2:]
nb.write(book,path)
p=root/'supplementary/update_b2_notebook.py'
s=p.read_text().replace('At $N=4$ the dense','At $N=6$ the dense')
p.write_text(s)
