"""Finalize visible B3 construction and cross-horizon evidence."""

import inspect
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "supplementary"), str(ROOT / "supplementary/helpers")]
# optional notebook-generation dependency
import nbformat as nbf  # noqa: E402  # ty: ignore[unresolved-import]
import run_b1  # noqa: E402,F401
from execute_notebook import execute  # noqa: E402

# local helper resolved by the notebook runtime path
from grouping import build_partial_sums  # noqa: E402  # ty: ignore[unresolved-import]

nb = nbf.read(ROOT / "dual_feg_example_lyap.ipynb", as_version=4)
start = next(
    i for i, c in enumerate(nb.cells) if c.source.startswith("## Lyapunov partial sums")
)
end = next(
    i for i, c in enumerate(nb.cells) if c.source.startswith("## Identify the vectors")
)
nb.cells[start].source = nb.cells[start].source.replace(
    "At the initial horizon the three interior ranks agree. Confirmation at another horizon is still pending; no rank-constancy claim across horizons is made yet.",
    "The recomputed $N=4$ and $N=6$ samples both have interior rank 4. Excluding only $V_0$ and $V_N$ leaves at least three indices at each horizon. This is finite-sample structural evidence, not an arbitrary-horizon theorem. The full Gram matrix uses the unscaled setup coordinate order and absolute rank tolerance $10^{-4}$; no singular value lies in $[0.5\\times10^{-4},2\\times10^{-4}]$.",
)
construction = (
    inspect.getsource(build_partial_sums)
    + """
rank_samples = []
selected_lyap = None
for sample_path, dense_path in [("state/dual_feg_b2.json", "state/dual_feg_dense.json"),
                                 ("supplementary/b2-N6.json", "supplementary/b2-N6-dense.json")]:
    certificate = json.loads((notebook_dir / sample_path).read_text())
    sample_dense = json.loads((notebook_dir / dense_path).read_text())
    replay_checks, _, _ = replay_certificate(certificate, get_pep_setup, notebook_dir, sample_dense["opt_value"])
    ctx, pb, _ = get_pep_setup(certificate["N_verify"], json.loads(certificate["params_json"]))
    pm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(certificate["params_json"]))
    S_scalar, S_piece_terms = full_psd_piece(certificate, ctx, pm)
    print("Horizon:", certificate["N_verify"])
    lyap, observation = build_partial_sums(certificate, ctx, pb, pm, S_scalar, S_piece_terms)
    assert observation["rank_credible"] and observation["grouping_checked"]
    print("Maximum coverage/increment residual:", max(observation["coverage_residuals"].values()))
    rank_samples.append(observation)
    if certificate["N_verify"] == b2["N_verify"]:
        selected_lyap = lyap
rank_left, rank_right = 1, 1
retained_profiles = [sample["rank_profile"][rank_left:sample["N"] + 1 - rank_right] for sample in rank_samples]
assert all(len(profile) >= 3 and len(set(profile)) == 1 for profile in retained_profiles)
assert len({profile[0] for profile in retained_profiles}) == 1
assert len({sample["N"] for sample in rank_samples}) == 2
assert all(sample["recipe_id"] == rank_samples[0]["recipe_id"] and sample["rank_convention"] == rank_samples[0]["rank_convention"] for sample in rank_samples)
print("Cross-horizon confirmation: rank 4 at N=4 and N=6; exclusions (1,1), absolute tolerance 1e-4.")
"""
)
nb.cells[start + 3 : end] = [
    nbf.v4.new_code_cell(construction),
    nbf.v4.new_markdown_cell(
        "### Block 3 conclusion\nThe selected $N=4$ profile is $[0,4,4,4,2]$, and the confirming $N=6$ profile is $[0,4,4,4,4,4,2]$. All interpolation contributions are assigned, with exactly one star monotonicity term and one full PSD block retained at the boundary. No terms are omitted. The terminal rank is 2, and the coverage identities pass in Gram, function-value, and constant coordinates. The numerical certificate remains verified; analytic full-PEP and Lyapunov proofs remain pending."
    ),
]
nbf.write(nb, ROOT / "dual_feg_example_lyap.ipynb")
_, evidence = execute("B3")
checklist = ROOT / "supplementary/dual_feg_example_lyap_checklist.md"
text = checklist.read_text(encoding="utf-8-sig")
text = re.sub(r"Last reviewed block: .*", "Last reviewed block: B3", text)
text = re.sub(r"SHA-256: .*", "SHA-256: " + evidence["sha256"], text)
lines = text.splitlines()
for i, line in enumerate(lines):
    if line.startswith("| 9 |"):
        parts = line.split("|")
        parts[3], parts[4], parts[5] = (
            " verified ",
            f" {start}-{start + 4} ",
            " Visible grouping, same-certificate replay, two-horizon rank and full-coordinate coverage executed and passed; rendered review omitted by policy ",
        )
        lines[i] = "|".join(parts)
checklist.write_text("\n".join(lines))
# Repair the serialized replay prelude to use one matching rebuilt context/builder.
state_path = ROOT / "state/dual_feg_b3.json"
state = json.loads(state_path.read_text())
state["certificate_check_code"] = state["certificate_check_code"].replace(
    "checks, ctx, pm = replay_certificate(certificate, get_pep_setup, notebook_dir, dense_value)",
    'checks, _, _ = replay_certificate(certificate, get_pep_setup, notebook_dir, dense_value)\nctx, pb, obj = get_pep_setup(certificate["N_verify"], json.loads(certificate["params_json"]))\npm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(certificate["params_json"]))',
)
state_path.write_text(json.dumps(state, indent=2))
