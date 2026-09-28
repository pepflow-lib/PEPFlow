from pathlib import Path
import nbformat as nbf
nb=nbf.read('pgm_example_lyap.ipynb',as_version=4)
for i,c in enumerate(nb.cells):
    print(i,c.cell_type,c.source.splitlines()[0][:120])
    if c.cell_type=='code' and i>=55:
        for o in c.outputs:
            if o.output_type=='stream': print(o.text[:3000])
