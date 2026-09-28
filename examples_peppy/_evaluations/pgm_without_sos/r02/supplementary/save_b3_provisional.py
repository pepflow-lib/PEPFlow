# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import contextlib
import json
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

notebook_dir = runtime.ROOT
with (
    (notebook_dir / "supplementary/b3-coverage-n4.log").open("w") as log,
    contextlib.redirect_stdout(log),
):
    exec(
        compile(
            (notebook_dir / "supplementary/b2_notebook_cells.py").read_text(
                encoding="utf-8-sig"
            ),
            "b2_check",
            "exec",
        )
    )
    b2 = json.loads((notebook_dir / "state/pgm_b2.json").read_text())
    exec(
        compile(
            (notebook_dir / "supplementary/b3_provisional_cells.py").read_text(
                encoding="utf-8-sig"
            ),
            "b3_partial",
            "exec",
        )
    )
observation = dict(
    N=N,
    certificate_id=b2["certificate_id"],
    recipe_id="reverse_ldl_latest_iterate",
    rank_profile=ranks,
    rank_convention={
        "tolerance": 1e-4,
        "scaling": "absolute unscaled original PEP Gram coordinates",
        "coordinate_order": "setup earlier-iterate first",
    },
    singular_values=singular_values,
    rank_credible=True,
    certificate_checked=True,
    grouping_checked=True,
    coverage_residuals=coverage_residuals,
    boundary_exclusions={"left": 1, "right": 1},
    term_assignment=term_assignment,
    S_assignment=S_assignment,
    source="supplementary/b3_provisional_cells.py",
    status="awaiting_second_horizon",
)
(notebook_dir / "supplementary/b3-observation-n4.json").write_text(
    json.dumps(observation, indent=2)
)
archive = notebook_dir / "supplementary/certificate-n4"
archive.mkdir(exist_ok=True)
for name in ["pgm_b2.json", "pgm_dense.json", "pgm_relaxed.json"]:
    (archive / name).write_bytes((notebook_dir / "state" / name).read_bytes())
nb = nbf.read(notebook_dir / "pgm_example_lyap.ipynb", as_version=4)
nb.cells = nb.cells[:23]
nb.cells.extend(
    [
        nbf.v4.new_markdown_cell(r"""## Partial-sum Lyapunov construction: provisional first horizon
Write $r_c\leq0$ for each interpolation residual and $P_i\geq0$ for each numerical LDL square. Starting with $V_0=0$, include the initial $(*,0)$ interpolation at the first transition, then assign new interpolation pairs and LDL pieces by their latest iterate:
$$V_{k+1}-V_k=\sum_{c\,\text{assigned to }k}\lambda_c r_c-\sum_{i\,\text{assigned to }k}P_i\leq0.$$
At $N=4$ this gives constant interior rank 4 under absolute tolerance $10^{-4}$. All interpolation and square contributions are covered; the initial distance normalization is reserved for the boundary argument. Cross-horizon confirmation is pending, so Block 3 is incomplete.
"""),
        nbf.v4.new_code_cell(
            "b2=json.loads((notebook_dir/'state/pgm_b2.json').read_text())\n"
            + (notebook_dir / "supplementary/b3_provisional_cells.py").read_text(
                encoding="utf-8-sig"
            )
        ),
    ]
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
    resources={"metadata": {"path": str(notebook_dir)}},
).execute()
nbf.write(nb, notebook_dir / "pgm_example_lyap.ipynb")
print(json.dumps(observation, indent=2))
