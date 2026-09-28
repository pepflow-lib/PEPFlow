# Notebook cells and source fragments executed below supply these globals.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import json
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
os.chdir(root)
sys.path.insert(0, str(root / "supplementary/helpers"))
# Configure validation-copy paths and runtime before the numerical imports.
import runtime  # noqa: E402, F401  # ty: ignore[unresolved-import]

# Preserve the runtime initialization before numerical imports.
# isort: split
import numpy as np  # noqa: E402 -- Initialize paths and runtime environment before importing.

# Selected cells execute in globals() and use these bindings.
import pepflow as pf  # noqa: E402, F401

# Preserve the bindings supplied to the selected exec cells.
# isort: split
from pgm_setup import get_pep_setup  # noqa: E402, F401  # ty: ignore[unresolved-import]

# isort: split
from pgm_setup import f, g  # noqa: E402, F401  # ty: ignore[unresolved-import]

notebook_dir = root
original = Path(
    "C:/Users/Jack/Documents/GitHub/PEPFlow/examples_peppy/_evaluations/20260923T140754Z_paper5_pgm_sos_6x5_isolation1/pgm_without_sos/r02"
)
nb = json.loads((root / "pgm_example_lyap.ipynb").read_text(encoding="utf-8-sig"))


def run_cell(i):
    source = "".join(nb["cells"][i]["source"])
    if i == 37:
        before = "source_path=Path(source).resolve()"
        after = "source_path=notebook_dir / Path(source).relative_to(original)"
        assert source.count(before) == 1
        source = source.replace(before, after)
    print("REPLAY CELL", i, flush=True)
    exec(compile(source, f"notebook-cell-{i}", "exec"), globals())


run_cell(37)
run_cell(38)
run_cell(41)
max_abs = lambda a: float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0))  # noqa: E731 -- Preserve the archived helper lambda.
run_cell(49)
b4 = json.loads((root / "state/pgm_b4.json").read_text())
coeff_by_k = {
    int(k): np.asarray(v, dtype=float).reshape(
        len(V_k_basis(int(k))), len(V_k_basis(int(k)))
    )
    for k, v in b4["coeff_by_k"].items()
}
function_coefficients = {int(k): v for k, v in b4["function_coefficients"].items()}
for k, C in coeff_by_k.items():
    assert np.allclose(C, C.T, atol=1e-7, rtol=0)
run_cell(53)
print("B4 saved coefficient reconstruction:", component_residuals, flush=True)
run_cell(56)
for i in [58, 60, 63, 65, 67, 69, 71, 73, 75, 77]:
    run_cell(i)
print("REPLAY COMPLETE; no solve or basis search", flush=True)
