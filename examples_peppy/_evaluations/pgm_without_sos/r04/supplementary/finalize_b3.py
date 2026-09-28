# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import numpy as np
import runtime
import sympy as sp
from pgm_setup import get_pep_setup

import pepflow as pf

notebook_dir = runtime.ATTEMPT
REPO_ROOT = runtime.APPROVED
certificate = json.loads((notebook_dir / "state/pgm_b2.json").read_text())
N_int = certificate["N_verify"]
params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.S.One, "R": sp.S.One}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
check_path = notebook_dir / "supplementary/b3_certificate_check.py"
check_code = check_path.read_text().replace(
    "from pepflow.constraint import ScalarConstraint, PSDConstraint",
    "from pepflow.constraint import ScalarConstraint",
)
check_code = check_code.replace(
    "certificate_diff = (pb.performance_metric",
    "assert pb.performance_metric is not None\ncertificate_diff = (pb.performance_metric",
)
check_path.write_text(check_code)
group_code = (notebook_dir / "supplementary/b3_grouping_cells.py").read_text(
    encoding="utf-8-sig"
)
decomposition_code, grouping_code = group_code.split("# CELL")
exec(compile(check_code, "b3_certificate_check.py", "exec"))
exec(compile(group_code, "b3_grouping_cells.py", "exec"))
workflow = (
    runtime.APPROVED
    / "plugins/pepflow-workflows/skills/lyap-define/references/workflow.md"
).read_text(encoding="utf-8-sig")
assess_code = next(
    chunk.split("```")[0]
    for chunk in workflow.split("```python\n")[1:]
    if "def assess_rank_pattern" in chunk.split("```")[0]
)
exec(compile(assess_code, "assess_rank_pattern", "exec"))
rank_samples = [
    json.loads(
        (notebook_dir / f"supplementary/sample_n{n}/observation.json").read_text()
    )
    for n in (4, 6)
]
rank_search = assess_rank_pattern(
    rank_samples, certificate["certificate_id"], left=1, right=1
)
assert rank_search["status"] == "confirmed"
assert rank_samples[0]["rank_profile"] == ranks
rank_search["evidence_path"] = "supplementary/rank_search.json"
(notebook_dir / "supplementary/rank_search.json").write_text(
    json.dumps(dict(summary=rank_search, samples=rank_samples), indent=2)
)
values = [pm.eval_scalar(V) for V in lyap]
state = {
    **certificate,
    "rank_profile": ranks,
    "rank_search": rank_search,
    "lyap_inner_prod_coords": [
        np.asarray(v.inner_prod_coords, float).tolist() for v in values
    ],
    "lyap_func_coords": [np.asarray(v.func_coords, float).tolist() for v in values],
    "lyap_offsets": [float(v.offset) for v in values],
    "certificate_check_code": check_code,
    "decomposition_code": decomposition_code,
    "grouping_code": grouping_code,
    "extra_duals": extra_duals,
    "rank_tolerance": 1e-4,
    "reconstruction_tolerance": 1e-4,
    "reconstruction_rtol": 1e-5,
    "grouping_coverage": dict(
        constraint_assignment=term_assignment,
        S_assignment={str(i): s for i, s in S_assignment.items()},
        normalization_constraint=tau_name,
        boundary_constraints=[],
        boundary_S=[],
        omitted_constraints=[],
        checked=True,
    ),
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(notebook_dir / "state/pgm_b3.json").write_text(
    json.dumps(state, indent=2, allow_nan=False)
)
prelude = """certificate = json.loads((notebook_dir / 'state/pgm_b2.json').read_text())
REPO_ROOT = repo_root
N_int = certificate['N_verify']
params_sp: dict[str, pf.NUMERICAL_TYPE] = {'L': sp.S.One, 'R': sp.S.One}
ctx, pb, obj = saved_get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
"""
summary_code = (
    assess_code
    + """
rank_samples = [json.loads((notebook_dir / f'supplementary/sample_n{n}/observation.json').read_text()) for n in (4, 6)]
rank_search = assess_rank_pattern(rank_samples, certificate['certificate_id'], left=1, right=1)
assert rank_search['status'] == 'confirmed'
assert rank_samples[0]['rank_profile'] == ranks
for observation in rank_samples:
    print('N=', observation['N'], 'ranks=', observation['rank_profile'], 'credible=', observation['rank_credible'])
print('Confirmed interior rank:', rank_search['rank'], 'horizons:', rank_search['confirmed_horizons'])
print('Absolute threshold 1e-4 in the setup coordinate order; fixed exclusions (1,1).')
"""
)
nb_path = notebook_dir / "pgm_example_lyap.ipynb"
nb = nbf.read(nb_path, as_version=4)
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum")
)
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Identify the vectors")
)
nb.cells[start:end] = [
    nbf.v4.new_markdown_cell(r"""## Partial-sum Lyapunov construction and ranks
Write each normalized interpolation residual as $I_c\leq0$ and each reverse-LDL remainder piece as $Q_i\geq0$. Starting at $V_0=0$, assign the optimizer-to-initial interpolation and the initial LDL pieces to the first increment. At each later iterate, assign the new optimizer and consecutive interpolation terms, and the two LDL pieces whose latest gradient has that iterate index:
$$V_{k+1}-V_k=\sum_{c\text{ assigned at }k}\lambda_c I_c-\sum_{i\text{ assigned at }k}Q_i\leq0.$$
The construction includes every interpolation contribution and every remainder piece. The normalization constraint is reserved for the final boundary argument. Both $N=4$ and $N=6$ have interior rank four when one index at each end is excluded; this is finite-sample evidence, not an analytic theorem. Small numerical pieces are retained."""),
    nbf.v4.new_code_cell(
        check_code.replace(
            "certificate_checked = False", prelude + "certificate_checked = False"
        )
    ),
    nbf.v4.new_markdown_cell(
        "### Numerical remainder pieces\nReuse the selected complete LDL decomposition. Its reconstruction and piece signs are checked before grouping."
    ),
    nbf.v4.new_code_cell(decomposition_code),
    nbf.v4.new_code_cell(grouping_code),
    nbf.v4.new_markdown_cell(
        "### Cross-horizon check\nBoth observations were recomputed from their own complete certificates using the identical saved construction. The N=6 selected sparse solve was optimal; its dense comparison solve was optimal_inaccurate, with the status retained. Selected-certificate identities and signs passed the unchanged tolerances at both horizons. Singular values are saved with each observation, including values below the rank threshold."
    ),
    nbf.v4.new_code_cell(summary_code),
]
nbf.write(nb, nb_path)
print("B3 complete:", rank_search)
