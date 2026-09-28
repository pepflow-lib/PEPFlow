from pathlib import Path
import nbformat
r=Path(__file__).resolve().parents[1]
p=r/'supplementary/helpers/derive_coefficients.py'
s=p.read_text().replace('import sympy as sp','from typing import cast\nimport sympy as sp').replace('K,NN,LL,','K,').replace('j,n,ell=map(sp.sympify,(j,n,ell))','j,n,ell=(cast(sp.Expr,sp.sympify(v)) for v in (j,n,ell))')
p.write_text(s)
nb=nbformat.read(r/'pgm_example_lyap.ipynb',as_version=4)
for c in nb.cells:
 if c.cell_type!='code':continue
 c.source=c.source.replace('"""Exact local scalar identities for proximal gradient."""','# Exact local scalar identities for proximal gradient.').replace('from typing import Any','from typing import Any, cast').replace('j,n,ell=map(sp.sympify,(j,n,ell))','j,n,ell=(cast(sp.Expr,sp.sympify(v)) for v in (j,n,ell))')
nbformat.write(nb,r/'pgm_example_lyap.ipynb')