from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

root = Path.cwd()
p = root / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(p, as_version=4)
for c in nb.cells:
    if c.cell_type == "code":
        c.source = c.source.replace(
            'pm_cert = pf.ExpressionManager(ctx_cert, resolve_parameters={"L": 1, "R": 1})',
            'pm_cert = pf.ExpressionManager(ctx_cert, resolve_parameters={"L": sp.Integer(1), "R": sp.Integer(1)})',
        )
nbformat.write(nb, p)
