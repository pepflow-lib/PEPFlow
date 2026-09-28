from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
path = root / "pgm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
pos = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum Lyapunov")
)
nb.cells[pos:pos] = [
    nbf.v4.new_markdown_cell("""### Additional B2 certificate for cross-horizon confirmation
A separate sample at $N=6$ uses the same sparse recipe and supplied SOS. The dense diagnostic reports `optimal_inaccurate`; its bound differs from the conjecture by about $4.2\times10^{-9}$. The selected sparse certificate reports `optimal` and independently passes the full identity and cone checks. Its complete components are saved separately; the selected $N=4$ handoff is unchanged."""),
    nbf.v4.new_code_cell("""b2_n6 = json.loads((notebook_dir / "supplementary/b2-n6-certificate.json").read_text())
dense_n6 = json.loads((notebook_dir / "supplementary/b2-n6-dense.json").read_text())
checks_n6, _, _, _ = verify(b2_n6, dense_n6["opt_value"], b2_n6["numerical_decomposition"])
assert checks_n6["passed"]
fit_n6 = []
for name,value in b2_n6["named_dual_values"].items():
    if name == "initial_condition":
        continue
    owner,pair = name.split(":")
    left,right = pair.split(",")
    fit_n6.append(abs(float(lambda_candidate(owner,left,right,6))-(value or 0.0)))
assert max(fit_n6)<=1e-4
print("N=6 candidate multiplier discrepancy:",max(fit_n6))
print("N=6 certificate checks:", checks_n6)
print("Dense status:",dense_n6["certificate_provenance"]["solver_status"])
print("Selected status:",b2_n6["certificate_provenance"]["solver_status"])"""),
]
nbf.write(nb, path)
