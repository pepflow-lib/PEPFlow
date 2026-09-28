"""Add the second certificate sample to the existing B2 notebook section."""
import sys
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supplementary"))
from execute_notebook import execute  # noqa: E402

nb = nbf.read(ROOT / "dual_feg_example_lyap.ipynb", as_version=4)
start = next(i for i, c in enumerate(nb.cells) if c.source.startswith("## Lyapunov partial sums"))
nb.cells[start:start] = [nbf.v4.new_markdown_cell("### Second complete certificate sample\nBlock 3 requested a fresh $N=6$ certificate for later rank comparison. The same structural relaxation preserves the dense optimum. The selected main certificate remains $N=4$. The following replay checks all components of the additional saved certificate; rank analysis of this sample belongs to the next B3 continuation."),
    nbf.v4.new_code_cell('sample6 = json.loads((notebook_dir / "supplementary/b2-N6.json").read_text())\ndense6 = json.loads((notebook_dir / "supplementary/b2-N6-dense.json").read_text())\nchecks6, _, _, _ = verify_certificate(sample6, get_pep_setup, dense6["opt_value"])\nassert checks6["passed"]\nprint("N=6 dense and sparse bounds:", dense6["opt_value"], sample6["opt_value"])\nprint("N=6 full numerical checks:", checks6)\nprint("N=6 candidate comparisons:", sample6["closed_form_search"]["N6_comparison"])')]
nbf.write(nb, ROOT / "dual_feg_example_lyap.ipynb")
execute("B2-N6")
