import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat as nb
root=runtime.ATTEMPT
path=root/'pgm_example_lyap.ipynb'
book=nb.read(path,as_version=4)
for cell in book.cells:
    if cell.cell_type=='code':
        cell.source=cell.source.replace(': continue',':\n        continue')
        cell.source=cell.source.replace("x=ctx_b2[f'x_{k}'];xs=ctx_b2['x_star']","x=ctx_b2[f'x_{k}']\n        xs=ctx_b2['x_star']")
        cell.source=cell.source.replace('params_sp={"L":sp.S.One,"R":sp.S.One}','params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L":sp.S.One,"R":sp.S.One}')
nb.write(book,path)
