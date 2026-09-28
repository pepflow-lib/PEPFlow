"""Compare verified horizons, save B3 state, and expose the construction."""

import hashlib
import json
import runpy
import sys
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import numpy as np

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = Path.cwd()
sys.argv = ["supplementary/b3_probe.py"]
scope = runpy.run_path(str(root / "supplementary/b3_probe.py"))
certificate = scope["certificate"]
samples = [
    json.loads((root / f"supplementary/b3-observation-N{n}.json").read_text())
    for n in (4, 6)
]
left, right = 1, 1
for sample in samples:
    assert (
        sample["certificate_checked"]
        and sample["grouping_checked"]
        and sample["rank_credible"]
    )
    assert sample["recipe_id"] == samples[0]["recipe_id"]
    assert sample["rank_convention"] == samples[0]["rank_convention"]
    retained = sample["rank_profile"][left : sample["N"] + 1 - right]
    assert len(retained) >= 3 and len(set(retained)) == 1
assert len({s["N"] for s in samples}) >= 2
assert len({s["rank_profile"][left] for s in samples}) == 1
rank_search = dict(
    status="confirmed",
    boundary_exclusions={"left": left, "right": right},
    rank=2,
    confirmed_horizons=[4, 6],
    selected_certificate_id=certificate["certificate_id"],
    recipe_id=samples[0]["recipe_id"],
    rank_convention=samples[0]["rank_convention"],
    unresolved_samples=[],
    evidence_path="supplementary/rank_search.json",
)
(root / "supplementary/rank_search.json").write_text(
    json.dumps({"summary": rank_search, "samples": samples}, indent=2)
)
source = (root / "supplementary/b3_probe.py").read_text()
check_code = source.split("# BEGIN CERTIFICATE CHECK\n")[1].split(
    "# END CERTIFICATE CHECK"
)[0]
decomposition_code = source.split("# BEGIN DECOMPOSITION\n")[1].split(
    "# END DECOMPOSITION"
)[0]
grouping_code = source.split("# BEGIN GROUPING\n")[1].split("# END GROUPING")[0]
pm = scope["pm"]
evaluated = [pm.eval_scalar(v) for v in scope["lyap"]]
state = {
    **certificate,
    "rank_profile": scope["ranks"],
    "rank_search": rank_search,
    "lyap_inner_prod_coords": [
        np.asarray(v.inner_prod_coords, float).tolist() for v in evaluated
    ],
    "lyap_func_coords": [np.asarray(v.func_coords, float).tolist() for v in evaluated],
    "lyap_offsets": [float(v.offset) for v in evaluated],
    "certificate_check_code": "import hashlib\nfrom certificate_tools import check_saved, entries_for\n"
    + check_code,
    "decomposition_code": decomposition_code,
    "grouping_code": grouping_code,
    "extra_duals": {},
    "rank_tolerance": 1e-4,
    "reconstruction_tolerance": 1e-4,
    "reconstruction_rtol": 1e-5,
    "grouping_coverage": {
        "constraint_assignment": scope["term_assignment"],
        "S_assignment": scope["S_assignment"],
        "normalization_constraint": "initial_condition",
        "boundary_constraints": scope["boundary_names"],
        "boundary_S": scope["boundary_S"],
        "omitted_constraints": [],
        "checked": True,
    },
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(root / "state/feg_b3.json").write_text(json.dumps(state, indent=2, allow_nan=False))
notebook = root / "feg_example_lyap.ipynb"
nb = nbf.read(notebook, as_version=4)
cells = [
    nbf.v4.new_markdown_cell(r"""## Block 3: Lyapunov partial sums
Write $\operatorname{Mon}(u,v)=-\langle A(u)-A(v),u-v\rangle\le0$ and $\operatorname{Lip}(u,v)=\|A(u)-A(v)\|^2-L^2\|u-v\|^2\le0$.
Starting from $V_0=0$, the saved numerical weights give
$$V_{k+1}-V_k=\lambda_k\operatorname{Mon}(x_k,x_{k+1})+\mu_{k+1}\operatorname{Lip}(x_{k+1},x_{k+1/2}),$$
with the monotonicity term absent for $k=0$. Nonnegative multipliers make this convention nonincreasing. We leave the terminal $(x_N,x_\star)$ monotonicity term and the complete PSD remainder $S$ at the boundary; no weighted contribution is omitted.

The original complete LDL is retained as one PSD boundary block. The failed analytic square guess is not used. The partial sums have rank two at every nonzero index at horizons 4 and 6. The fixed comparison excludes $V_0,V_N$ and retains at least three indices per horizon. This is finite-sample discovery evidence, not a universal proof."""),
    nbf.v4.new_code_cell(
        'import hashlib\ncertificate = b2\nparams_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.S(1), "R": sp.S(1)}\nctx, pb, obj = get_pep_setup(N_int, params_sp)\npb.set_relaxed_constraints(certificate["relaxed_constraints"])\npm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)\n'
        + check_code
        + '\nprint("Replayed complete certificate:", certificate_checked)\nprint(checks["residuals"])'
    ),
    nbf.v4.new_code_cell(
        decomposition_code
        + '\nprint("Complete-S block reconstruction error:", np.max(np.abs(decomposition_residual)))'
    ),
    nbf.v4.new_code_cell(grouping_code),
    nbf.v4.new_code_cell(
        'rank_evidence = json.loads((notebook_dir / "supplementary/rank_search.json").read_text())\nfor sample in rank_evidence["samples"]:\n    retained = sample["rank_profile"][1:sample["N"]]\n    assert len(retained) >= 3 and set(retained) == {2}\n    print(f"N={sample[\'N\']}: rank 2 at {len(retained)} retained indices; certificate and coverage checked")\nprint("Fixed exclusions: (1,1); absolute unscaled rank tolerance: 1e-4")\nprint("Selected coverage:", grouping_checked, "boundary interpolation terms:", len(boundary_names), "boundary PSD blocks:", len(boundary_S))'
    ),
]
for i, c in enumerate(cells):
    c.id = f"b3-{i:02d}"
start = next(i for i, c in enumerate(nb.cells) if c.id in ("b1-08", "b3-00"))
end = next(i for i, c in enumerate(nb.cells) if c.id == "b1-09")
nb.cells[start:end] = cells
nbf.write(nb, notebook)
NotebookClient(
    nb, timeout=120, kernel_name="attempt", resources={"metadata": {"path": str(root)}}
).execute()
nbf.write(nb, notebook)
markdown = "\n".join(c.source for c in nb.cells if c.cell_type == "markdown")
assert not any(x in markdown for x in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r"))
checklist = root / "supplementary/feg_example_lyap_checklist.md"
lines = checklist.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B3"
    elif line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(notebook.read_bytes()).hexdigest()
    elif line.startswith("| 9 |"):
        lines[i] = (
            "| 9 | partial-sum Lyapunov construction and rank profile | verified | b3-00 through b3-04 | Complete certificate replay, visible grouping/coverage/PSD checks, rank 2 confirmed at N=4,6 with fixed exclusions (1,1), tolerance 1e-4. |"
        )
checklist.write_text("\n".join(lines) + "\n")
print(
    json.dumps({"B3": "complete", "rank_search": rank_search, "fresh_kernel": "passed"})
)
