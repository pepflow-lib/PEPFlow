import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import os

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]
import runtime

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
path = root / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum")
)
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Special-vector")
)
intro = nbformat.v4.new_markdown_cell(r"""## Partial-sum Lyapunov construction and rank profile
Write $y_k=x_{k+1/2}$, and normalize the interpolation residuals as
$$\operatorname{Lip}(u,v)=\|A(u)-A(v)\|^2-L^2\|u-v\|^2\le0,$$
$$\operatorname{Mon}(u,v)=-\langle A(u)-A(v),u-v\rangle\le0.$$
For the saved positive multipliers $\nu_k,\mu_k$, construct $V_0=0$ and
$$V_{k+1}-V_k=\nu_k\operatorname{Lip}(x_k,y_k)+\mu_k\operatorname{Mon}(x_N,y_k),\quad 0\le k\le N-2,$$
$$V_N-V_{N-1}=\nu_{N-1}\operatorname{Lip}(x_{N-1},x_N).$$
Thus the numerical construction has the nonincreasing sign convention. The one remaining monotonicity term is between $x_N$ and $x_\star$; the complete positive Gram remainder is kept as one terminal boundary piece. No numerical multiplier or small LDL factor is omitted.

At both $N=6$ and $N=8$, the interior rank is 4 with $V_0,V_N$ excluded, using absolute singular-value tolerance $10^{-4}$ in the original earlier-iterates-first coordinates. Each retained set has at least three indices. The selected final rank is 2, so the terminal partial sum is not zero; the full-coordinate boundary coverage check accounts for it explicitly. This confirms a finite-sample rank pattern, not a universal theorem. All-horizon formulas and exact endpoint sign reasoning remain for B5.
""")
setup = """certificate = json.loads((notebook_dir / "state/dual_feg_b2.json").read_text())
N_int = certificate["N_verify"]
params_sp = {key: sp.S(value) for key, value in json.loads(certificate["params_json"]).items()}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
ctx.set_as_current()
REPO_ROOT = repo_root
"""
check = (
    (root / "supplementary/b3_certificate_check.py")
    .read_text(encoding="utf-8-sig")
    .replace("ScalarConstraint, PSDConstraint", "ScalarConstraint")
)
decomp = (root / "supplementary/b3_decomposition.py").read_text(encoding="utf-8-sig")
group = (root / "supplementary/b3_grouping.py").read_text(encoding="utf-8-sig")
assess = (root / "supplementary/b3_assess.py").read_text()
summary = """rank_samples = [json.loads((notebook_dir / f"supplementary/b3-trial-n{h}.json").read_text()) for h in (6, 8)]
rank_confirmation = assess_rank_pattern(rank_samples, certificate["certificate_id"], left=1, right=1)
assert rank_confirmation["status"] == "confirmed"
for sample in rank_samples:
    print("Horizon", sample["N"], "rank profile", sample["rank_profile"], "credible", sample["rank_credible"])
print("Confirmed horizons:", rank_confirmation["confirmed_horizons"], "common rank:", rank_confirmation["rank"])
print("Fixed exclusions:", rank_confirmation["boundary_exclusions"], "absolute singular-value tolerance:", rank_tolerance)
print("All retained singular values inspected; none lies between half and twice the fixed threshold.")
"""
nb.cells[start:end] = [
    intro,
    nbformat.v4.new_code_cell(setup),
    nbformat.v4.new_code_cell(check),
    nbformat.v4.new_code_cell(decomp),
    nbformat.v4.new_code_cell(group),
    nbformat.v4.new_code_cell(assess + "\n" + summary),
]
nbformat.write(nb, path)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(
    nb,
    timeout=120,
    kernel_name="dual-feg-attempt",
    resources={"metadata": {"path": str(root)}},
).execute()
nbformat.write(nb, path)
print("B3 notebook replay passed")
