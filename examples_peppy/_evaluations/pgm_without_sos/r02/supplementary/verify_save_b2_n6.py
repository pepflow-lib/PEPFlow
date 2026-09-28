# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import contextlib
import os

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]
from pgm_setup import (  # noqa: F401 -- Required by exec of b2_notebook_cells.py.
    get_pep_setup,
)

root = runtime.ROOT
notebook_dir = root
source = (root / "supplementary/b2_notebook_cells.py").read_text(encoding="utf-8-sig")
source = source.replace(
    "state/pgm_dense.json", "supplementary/certificate-n6/pgm_dense.json"
).replace(
    "supplementary/b2-relaxation-001.json",
    "supplementary/certificate-n6/selected-raw.json",
)
(root / "supplementary/b2_notebook_cells_n6.py").write_text(source)
with (
    (root / "supplementary/certificate-n6/verification.log").open("w") as log,
    contextlib.redirect_stdout(log),
):
    exec(compile(source, "b2_n6", "exec"))
    save = (root / "supplementary/save_b2.py").read_text(encoding="utf-8-sig")
    save = save.replace(
        "supplementary/b2_notebook_cells.py", "supplementary/b2_notebook_cells_n6.py"
    ).replace(
        "notebook_dir/'state'/filename",
        "notebook_dir/'supplementary/certificate-n6'/filename",
    )
    exec(compile(save, "save_b2_n6", "exec"))
nb = nbf.read(root / "pgm_example_lyap.ipynb", as_version=4)
nb.cells = nb.cells[:25]
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## Additional Block 2 sample: $N=6$
The same sparse constraint recipe is applied to a new complete solve. The dense baseline returned `optimal_inaccurate`, with objective close to the candidate; the selected sparse certificate returned `optimal`. All multipliers, the Gram dual matrix and normalization below come from that single selected solve. The $N=4$ sample remains the selected main state while this complete sample is archived for the required rank comparison. The initial formula search is reused and its candidates are checked again at this horizon.
""")
)
for chunk in source.split("# %% ")[1:]:
    heading, code = chunk.split("\n", 1)
    nb.cells.extend(
        [nbf.v4.new_markdown_cell("### " + heading), nbf.v4.new_code_cell(code)]
    )
for title in [
    "Special-vector identification",
    "Coefficient extraction and closed-form V_k",
    "Symbolic step, base, and boundary identities",
]:
    nb.cells.append(nbf.v4.new_markdown_cell("## " + title + "\nPending later blocks."))
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(
    nb,
    timeout=180,
    kernel_name="pgm-private",
    resources={"metadata": {"path": str(root)}},
).execute()
nbf.write(nb, root / "pgm_example_lyap.ipynb")
print("N6 complete certificate verified; notebook executed.")
print("Residuals:", residuals)
