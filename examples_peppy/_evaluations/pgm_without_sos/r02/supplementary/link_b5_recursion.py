from pathlib import Path
import nbformat as nbf
p=Path('pgm_example_lyap.ipynb')
nb=nbf.read(p,as_version=4)
cell=nb.cells[75]
cell.source=cell.source.replace("print('checking coefficient',flush=True)","derived_beta=sp.factor(m-v*v/a-(w-e*v/a)**2/delta)\nassert sp.cancel(rec-beta_recurrence(k,(t+k)/2,c))==0\nprint('Solved final-pivot equation for beta_k:',derived_beta,flush=True)\nprint('checking coefficient',flush=True)")
cell.outputs=[]
cell.execution_count=None
nbf.write(nb,p)
p=Path('supplementary/b5_symbolic_cells.py')
s=p.read_text().replace("print('checking coefficient',flush=True)","derived_beta=sp.factor(m-v*v/a-(w-e*v/a)**2/delta)\nassert sp.cancel(rec-beta_recurrence(k,(t+k)/2,c))==0\nprint('Solved final-pivot equation for beta_k:',derived_beta,flush=True)\nprint('checking coefficient',flush=True)")
p.write_text(s)
