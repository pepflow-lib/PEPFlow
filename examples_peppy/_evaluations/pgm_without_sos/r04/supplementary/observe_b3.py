# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np
import runtime
import sympy as sp
from pgm_setup import get_pep_setup

import pepflow as pf

notebook_dir = runtime.ATTEMPT
REPO_ROOT = runtime.APPROVED
certificate_path = notebook_dir / (
    sys.argv[1] if len(sys.argv) > 1 else "state/pgm_b2.json"
)
certificate = json.loads(certificate_path.read_text())
N_int = certificate["N_verify"]
params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.S.One, "R": sp.S.One}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
check_source = (notebook_dir / "supplementary/b3_certificate_check.py").read_text()
group_source = (notebook_dir / "supplementary/b3_grouping_cells.py").read_text(
    encoding="utf-8-sig"
)
exec(compile(check_source, "b3_certificate_check.py", "exec"))
exec(compile(group_source, "b3_grouping_cells.py", "exec"))
observation = dict(
    N=N_int,
    certificate_id=certificate["certificate_id"],
    recipe_id="reverse_ldl_latest_iterate_v1",
    rank_profile=ranks,
    singular_values=singular_values,
    rank_convention=dict(
        tolerance=1e-4,
        scaling="absolute",
        coordinate_order="setup basis: earlier iterates first",
    ),
    rank_credible=all(not any(5e-5 <= s <= 2e-4 for s in ss) for ss in singular_values),
    certificate_checked=certificate_checked,
    grouping_checked=grouping_checked,
    coverage_residuals=coverage_residuals,
    boundary_exclusions=dict(left=1, right=1),
    constraint_assignment=term_assignment,
    S_assignment=S_assignment,
)
archive = notebook_dir / "supplementary" / f"sample_n{N_int}"
archive.mkdir(exist_ok=True)
(archive / "certificate.json").write_text(json.dumps(certificate, indent=2))
(archive / "observation.json").write_text(json.dumps(observation, indent=2))
evals = [pm.eval_scalar(v) for v in lyap]
(archive / "partial_sums.json").write_text(
    json.dumps(
        dict(
            gram=[np.asarray(v.inner_prod_coords, float).tolist() for v in evals],
            function=[np.asarray(v.func_coords, float).tolist() for v in evals],
            offset=[float(v.offset) for v in evals],
        ),
        indent=2,
    )
)
print("Observation preserved:", archive)
