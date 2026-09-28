"""Assess already recomputed horizon trials and preserve the selected B3 state."""

import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import numpy as np

root = Path(__file__).resolve().parents[1]
samples = [
    json.loads((root / f"supplementary/b3-trial-N{n}.json").read_text()) for n in (4, 6)
]
selected = samples[0]
for sample in samples:
    assert (
        sample["certificate_checked"]
        and sample["grouping_checked"]
        and sample["rank_credible"]
    )
    assert sample["recipe_id"] == selected["recipe_id"]
    assert sample["rank_convention"] == selected["rank_convention"]
    for kind in ("certificate_check", "decomposition", "grouping"):
        assert (
            sample[kind + "_code"] == (root / f"supplementary/b3_{kind}.py").read_text()
        )
    ranks = [
        int(np.linalg.matrix_rank(np.asarray(m), tol=1e-4))
        for m in sample["lyap_inner_prod_coords"]
    ]
    assert ranks == sample["rank_profile"]
    retained = ranks[1 : sample["N"]]
    assert len(retained) >= 3 and set(retained) == {4}
    values = np.array(sample["singular_values"][1:])
    sample["smallest_retained_singular_value"] = float(values[:, 3].min())
    sample["largest_discarded_singular_value"] = float(values[:, 4:].max())
    assert sample["smallest_retained_singular_value"] > 1e-3
    assert sample["largest_discarded_singular_value"] < 1e-5
    print(
        "Singular-value gap",
        sample["N"],
        sample["smallest_retained_singular_value"],
        sample["largest_discarded_singular_value"],
    )
summary = {
    "status": "confirmed",
    "boundary_exclusions": {"left": 1, "right": 1},
    "rank": 4,
    "confirmed_horizons": [4, 6],
    "selected_certificate_id": selected["certificate_id"],
    "recipe_id": selected["recipe_id"],
    "rank_convention": selected["rank_convention"],
    "unresolved_samples": [],
    "evidence_path": "supplementary/rank_search.json",
}
(root / "supplementary/rank_search.json").write_text(
    json.dumps({"summary": summary, "samples": samples}, indent=2)
)
b2 = json.loads((root / "state/bppm_b2.json").read_text())
assert b2["certificate_id"] == selected["certificate_id"]
b3 = {
    **b2,
    **{
        key: selected[key]
        for key in (
            "certificate_check_code",
            "decomposition_code",
            "grouping_code",
            "rank_profile",
            "lyap_inner_prod_coords",
            "lyap_func_coords",
            "lyap_offsets",
            "grouping_coverage",
        )
    },
    "rank_search": summary,
    "rank_tolerance": 1e-4,
    "extra_duals": {},
    "reconstruction_tolerance": 1e-4,
    "reconstruction_rtol": 1e-5,
    "completion_status": "pending_notebook_checks",
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(root / "state/bppm_b3.json").write_text(json.dumps(b3, indent=2))
dest = root / "bppm_example_lyap.ipynb"
nb = nbf.read(dest, as_version=4)
for c in nb.cells:
    if c.cell_type == "markdown" and c.source.startswith("## Lyapunov partial sums"):
        c.source = c.source.replace(
            "The first trial uses $N=4$. Rank and coverage at this horizon are discovery evidence; comparison with a second independently solved horizon is still required.",
            "The selected trial uses $N=4$. The same recipe is independently checked at $N=6$. Rank agreement is finite-sample discovery evidence; it does not yet prove an arbitrary-horizon theorem.",
        )
idx = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("### Cross-horizon status")
)
nb.cells[idx : idx + 1] = [
    nbf.v4.new_markdown_cell(
        "### Confirmed cross-horizon rank observation\n\nThe same grouping and complete-S boundary recipe gives ranks `[0, 4, 4, 4, 4]` at N=4 and `[0, 4, 4, 4, 4, 4, 4]` at N=6. Fixed exclusions `(1, 1)` retain three and five indices respectively. Ranks use absolute tolerance `1e-4` on unscaled matrices in each context’s original coordinate order. The singular-value gaps below show no near-threshold ambiguity. Every horizon has its own revalidated complete certificate and full-coordinate coverage evidence. The selected N=4 certificate is retained for B4."
    ),
    nbf.v4.new_code_cell(
        "rank_evidence = json.loads((notebook_dir / 'supplementary/rank_search.json').read_text())\nfor sample in rank_evidence['samples']:\n    rebuilt_ranks = [int(np.linalg.matrix_rank(np.asarray(m), tol=1e-4)) for m in sample['lyap_inner_prod_coords']]\n    assert rebuilt_ranks == sample['rank_profile']\n    retained = rebuilt_ranks[1:sample['N']]\n    assert len(retained) >= 3 and set(retained) == {4}\n    assert sample['certificate_checked'] and sample['grouping_checked']\n    print('N =', sample['N'], 'retained indices =', len(retained), 'common rank =', retained[0])\n    print('Smallest retained singular value:', sample['smallest_retained_singular_value'])\n    print('Largest discarded singular value:', sample['largest_discarded_singular_value'])\n    print('Coverage residual:', sample['coverage_residuals'])\nassert rank_evidence['summary']['selected_certificate_id'] == b2['certificate_id']\nprint('Rank observation confirmed at N=4 and N=6; analytic proof remains pending.')"
    ),
]
nbf.write(nb, dest)
