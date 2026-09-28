from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

root = Path.cwd()
p = root / "supplementary/b5_symbolic_cells.py"
s = p.read_text()
s = s.replace(
    "    reduction=lambda z: sp.factor(sp.cancel(z.subs(N_sp,(t_sp+k_sp)/2))) if name=='Step' else sp.factor(sp.cancel(z))",
    "    def reduction(z):\n        return sp.factor(sp.cancel(z.subs(N_sp,(t_sp+k_sp)/2))) if name=='Step' else sp.factor(sp.cancel(z))",
)
s = (
    s.replace(";d=", "\nd=")
    .replace(";e=", "\ne=")
    .replace(";v=", "\nv=")
    .replace(";w=", "\nw=")
)
p.write_text(s)
p = root / "supplementary/b5_comparison_cells.py"
s = p.read_text(encoding="utf-8-sig").replace("b4['S']", "b4['S_matrix']")
p.write_text(s)
nb = nbf.read(root / "pgm_example_lyap.ipynb", as_version=4)
for cell in nb.cells:
    if cell.cell_type == "code":
        cell.source = cell.source.replace(
            "    reduction=lambda z: sp.factor(sp.cancel(z.subs(N_sp,(t_sp+k_sp)/2))) if name=='Step' else sp.factor(sp.cancel(z))",
            "    def reduction(z):\n        return sp.factor(sp.cancel(z.subs(N_sp,(t_sp+k_sp)/2))) if name=='Step' else sp.factor(sp.cancel(z))",
        )
        cell.source = (
            cell.source.replace(";d=", "\nd=")
            .replace(";e=", "\ne=")
            .replace(";v=", "\nv=")
            .replace(";w=", "\nw=")
            .replace("b4['S']", "b4['S_matrix']")
        )
        if "from IPython.display import Math,display" in cell.source:
            cell.source = (
                "from IPython.display import Math,display\n"
                + cell.source.replace("from IPython.display import Math,display\n", "")
            )
nbf.write(nb, root / "pgm_example_lyap.ipynb")
