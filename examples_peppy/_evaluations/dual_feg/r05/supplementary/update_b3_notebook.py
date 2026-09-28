import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
s = json.loads((ROOT / "state/dual_feg_b3.json").read_text())
md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell
cells = [
    md(r"""## Lyapunov partial sums

Write $y_k=x_{k+1/2}$ and use normalized residuals
$$M_k=-\langle A(x_N)-A(y_k),x_N-y_k\rangle\leq0,\qquad
H_k=\|A(x_k)-A(y_k)\|^2-\|x_k-y_k\|^2\leq0.$$
At $L=1$, the selected numerical multipliers define
$$V_0=0,\qquad V_{k+1}-V_k=\lambda_k M_k+\mu_k H_k\quad(0\leq k<N-1).$$
The final increment is the selected Lipschitz residual between $x_{N-1}$ and $x_N$ with its multiplier. Every increment is nonpositive. Keep terminal-star monotonicity and the whole nonnegative $S$ as boundary leftovers. Using the entire saved remainder avoids replacing small numerical components by the rank-one candidate.

Reconstruction and coverage include all Gram, function, and constant components. The same construction has interior rank four at both tested horizons; this is discovery evidence rather than an all-horizon theorem."""),
    code(s["certificate_check_code"]),
    code(s["decomposition_code"]),
    code(
        s["grouping_code"]
        + """
for k,rank in enumerate(ranks):
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()
rank_left = rank_right = 1
retained = ranks[rank_left:N_int+1-rank_right]
print("Interior rank is constant at this N:", len(retained)>=3 and len(set(retained))==1, "boundary exclusions:", (rank_left,rank_right))
print("Full-coordinate coverage residuals:", observation["coverage_residuals"])
"""
    ),
    code("""rank_samples = []
for cert_path in [NOTEBOOK_DIR/"state/dual_feg_b2.json", NOTEBOOK_DIR/"supplementary/certificate_N8.json"]:
    sample_certificate = json.loads(cert_path.read_text())
    rank_samples.append(group(sample_certificate))
retained_profiles = [sample["rank_profile"][1:sample["N"]] for sample in rank_samples]
assert all(len(profile)>=3 and len(set(profile))==1 for profile in retained_profiles)
assert len({profile[0] for profile in retained_profiles})==1
assert all(sample["rank_credible"] and sample["certificate_checked"] and sample["grouping_checked"] for sample in rank_samples)
print("Confirmed horizons:", [sample["N"] for sample in rank_samples])
print("Common interior rank:", retained_profiles[0][0])
print("Fixed exclusions: V_0 and V_N; absolute rank tolerance 1e-4, unscaled Gram coordinates.")
print("Each sample includes checked certificate, coverage, and singular-value evidence.")
# Restore selected context after the independent confirmation sample.
ctx,pb,obj,pm,weighted_terms,S_scalar,certificate_residuals = recheck(certificate)"""),
]
index = next(
    i for i, c in enumerate(nb.cells) if c.source.startswith("## Lyapunov partial sums")
)
nb.cells[index : index + 1] = cells
nbformat.write(nb, path)
print("B3 cells", index, index + len(cells) - 1)
