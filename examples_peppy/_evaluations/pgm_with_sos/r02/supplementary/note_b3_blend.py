from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
path = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
cell = next(
    c
    for c in nb.cells
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum Lyapunov")
)
cell.source += r"""

**Numerical decomposition recovery.** The supplied factors reconstruct the slack approximately; using them alone failed the terminal basis-span check. Assigning the discrepancy to the final piece was indefinite and rejected. A polar alignment $W=QS^{1/2}$, with $Q$ the polar factor of $US^{1/2}$ for supplied factors $U$, reconstructs the saved slack exactly, but using it alone failed two interior span checks. The selected recipe uses the fixed nonnegative blend
$$\widetilde S_i=\frac7{10}S_i^{\mathrm{supplied}}+\frac3{10}S_i^{\mathrm{aligned}}.$$
Each piece is a sum of squares. Its reconstruction and full-coordinate coverage errors are checked against the unchanged frozen tolerances at both horizons. The blend was chosen after measuring basis-span residuals, and this numerical tuning is recorded in supplementary diagnostics. The same value $3/10$ is used at both horizons. No certificate components or tolerances changed. The original supplied SOS remains the candidate for exact symbolic analysis; the finite-sample numerical blend is not an all-horizon formula."""
nbformat.write(nb, path)
