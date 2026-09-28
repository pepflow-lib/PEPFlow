"""Fix symbolic display and finish labeled numerical certificate tables."""
from pathlib import Path
import nbformat
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"dual_feg_example_lyap.ipynb"
nb=nbformat.read(p,as_version=4)
for c in nb.cells:
    if c.cell_type=="code" and "C_formula.tolist()" in c.source:
        c.source=c.source.replace('row_labels=["a","z_{k}","x_{k}-x_{N}","x_{0}-x_{N}"])','row_labels=["a","z_{k}","x_{k}-x_{N}","x_{0}-x_{N}"],precision=0)')
    if c.cell_type=="code" and c.source.startswith('dense = json.loads'):
        c.source += """
for data,label in [(dense,"dense"),(certificate,"selected sparse")]:
    for family in sorted({m["group"] for m in data["constraint_metadata"].values() if m["group"]}):
        significant = [(name,val) for name,val in data["named_dual_values"].items()
                       if data["constraint_metadata"][name]["group"]==family and val is not None and abs(val)>1e-6]
        print(label,family,"labeled significant duals; display cutoff 1e-6 only.")
        pf.pprint_labeled_matrix(np.array([[v] for _,v in significant]),
            row_labels=[name for name,_ in significant],column_labels=["dual"],precision=8)
"""
nbformat.write(nb,p)

