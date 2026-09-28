# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json
import os

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]
from pgm_setup import (  # noqa: F401 -- Required by exec of b3_check_code.py.
    get_pep_setup,
)

notebook_dir = runtime.ROOT
certificate = json.loads((notebook_dir / "state/pgm_b2.json").read_text())
source_names = ["b3_check_code.py", "b3_decomposition_code.py", "b3_grouping_code.py"]
sources = [
    (notebook_dir / "supplementary" / name).read_text(encoding="utf-8-sig")
    for name in source_names
]
for source, name in zip(sources, source_names):
    exec(compile(source, name, "exec"))
samples = json.loads((notebook_dir / "supplementary/b3-comparison.json").read_text())
assert len({s["N"] for s in samples}) == len(samples) >= 2
assert all(
    s["recipe_id"] == samples[0]["recipe_id"]
    and s["rank_convention"] == samples[0]["rank_convention"]
    for s in samples
)
retained = [s["rank_profile"][1 : s["N"]] for s in samples]
assert all(len(r) >= 3 and len(set(r)) == 1 for r in retained)
assert len({r[0] for r in retained}) == 1
assert all(
    s["certificate_checked"] and s["grouping_checked"] and s["rank_credible"]
    for s in samples
)
selected_observation = next(
    s for s in samples if s["certificate_id"] == certificate["certificate_id"]
)
assert selected_observation["rank_profile"] == ranks
rank_search = dict(
    status="confirmed",
    boundary_exclusions={"left": 1, "right": 1},
    rank=retained[0][0],
    confirmed_horizons=sorted(s["N"] for s in samples),
    selected_certificate_id=certificate["certificate_id"],
    recipe_id=samples[0]["recipe_id"],
    rank_convention=samples[0]["rank_convention"],
    unresolved_samples=[],
    evidence_path="supplementary/rank_search.json",
)
(notebook_dir / "supplementary/rank_search.json").write_text(
    json.dumps({"summary": rank_search, "samples": samples}, indent=2)
)
evaluated = [pm.eval_scalar(v) for v in lyap]
state = {
    **certificate,
    "rank_profile": ranks,
    "rank_search": rank_search,
    "lyap_inner_prod_coords": [
        np.asarray(v.inner_prod_coords, dtype=float).tolist() for v in evaluated
    ],
    "lyap_func_coords": [
        np.asarray(v.func_coords, dtype=float).tolist() for v in evaluated
    ],
    "lyap_offsets": [float(v.offset) for v in evaluated],
    "certificate_check_code": sources[0],
    "decomposition_code": sources[1],
    "grouping_code": sources[2],
    "extra_duals": extra_duals,
    "rank_tolerance": 1e-4,
    "reconstruction_tolerance": 1e-4,
    "reconstruction_rtol": 1e-5,
    "grouping_coverage": {
        "constraint_assignment": term_assignment,
        "S_assignment": {str(k): v for k, v in S_assignment.items()},
        "normalization_constraint": tau_name,
        "boundary_constraints": [],
        "boundary_S": [],
        "omitted_constraints": [],
        "checked": True,
    },
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(notebook_dir / "state/pgm_b3.json").write_text(
    json.dumps(state, indent=2, allow_nan=False)
)
nb = nbf.read(notebook_dir / "pgm_example_lyap.ipynb", as_version=4)
# Preserve both B2 sections, replacing only the provisional B3 material.
nb.cells = nb.cells[:23]
nb.cells.append(
    nbf.v4.new_markdown_cell(
        "## Additional Block 2 sample: N=6\nThe dense baseline is optimal_inaccurate; the selected sparse solve is optimal. All selected components come from one solve."
    )
)
n6_cells_source = (notebook_dir / "supplementary/b2_notebook_cells_n6.py").read_text(
    encoding="utf-8-sig"
)
for chunk in n6_cells_source.split("# %% ")[1:]:
    heading, cell_source = chunk.split("\n", 1)
    nb.cells.extend(
        [nbf.v4.new_markdown_cell("### " + heading), nbf.v4.new_code_cell(cell_source)]
    )
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""## Partial-sum Lyapunov construction and rank profile
Let $r_c\leq0$ be the normalized interpolation residuals and $P_i\geq0$ the retained LDL squares of each horizon's own certificate. Starting from $V_0=0$, we assign interpolation terms by their destination iterate and squares by their latest supported iterate (support cutoff $10^{-5}$ is used only for assignment; no coefficients are discarded). The initial $(*,0)$ term enters the first transition:
$$V_{k+1}-V_k=\sum_{c\text{ assigned at }k}\lambda_c r_c-\sum_{i\text{ assigned at }k}P_i\leq0.$$
All interpolation contributions and all squares enter by $V_N$; the initial-distance normalization remains for the boundary proof. Thus $V_N$ has a distance-square component, which need not have rank zero. The following visible construction rebuilds and rechecks each complete saved certificate without solving.
""")
)
function_source = "def reconstruct_partial_sums(certificate):\n" + "".join(
    "    " + line + "\n" for line in "\n".join(sources).splitlines()
)
function_source += '    return {"N": N, "certificate_id": certificate["certificate_id"], "rank_profile": ranks, "coverage": coverage_residuals, "credible": rank_credible, "certificate_checked": certificate_checked, "grouping_checked": grouping_checked, "boundary_names": boundary_names, "boundary_S": boundary_S}\n'
nb.cells.append(nbf.v4.new_code_cell(function_source))
nb.cells.append(
    nbf.v4.new_code_cell("""rank_observations=[]
for relative_path in ['state/pgm_b2.json','supplementary/certificate-n6/pgm_b2.json']:
    saved_certificate=json.loads((notebook_dir/relative_path).read_text())
    rank_observations.append(reconstruct_partial_sums(saved_certificate))
retained_profiles=[row['rank_profile'][1:row['N']] for row in rank_observations]
assert len({row['N'] for row in rank_observations})==2
assert all(len(profile)>=3 and len(set(profile))==1 for profile in retained_profiles)
assert len({profile[0] for profile in retained_profiles})==1
assert all(row['credible'] for row in rank_observations)
print('Confirmed horizons:',[row['N'] for row in rank_observations])
print('Common interior rank:',retained_profiles[0][0],'; fixed exclusions:',(1,1),'; absolute tolerance:',1e-4)
""")
)
nb.cells.append(
    nbf.v4.new_markdown_cell(r"""The rank profiles are $[0,4,4,4,1]$ at $N=4$ and $[0,4,4,4,4,4,1]$ at $N=6$. We exclude one index at each end for comparison, retaining three and five interior indices respectively. The numerical rank uses the unscaled original Gram coordinates and absolute threshold $10^{-4}$. No singular value lies in the diagnostic interval $[10^{-5},10^{-3}]$.
The N=4 certificate remains the selected handoff. Complete function-value and constant coordinates are preserved with every $V_k$. These finite-sample checks do not establish an arbitrary-horizon theorem; basis reconstruction and exact proof are still pending.
""")
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
print("B3 saved, notebook executed, selected N=4.")
