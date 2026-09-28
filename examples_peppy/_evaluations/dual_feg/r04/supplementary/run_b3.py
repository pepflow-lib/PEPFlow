# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Revalidate one B2 certificate and explore its B3 rank profile, without solving."""

import json
import os
import sys
from pathlib import Path

notebook_dir = Path(__file__).resolve().parents[1]
REPO_ROOT = notebook_dir / "supplementary/approved"
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "MPLCONFIGDIR",
    "IPYTHONDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    p = notebook_dir / "supplementary/.runtime" / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
sys.path[:0] = [
    str(REPO_ROOT),
    str(notebook_dir / "supplementary/helpers"),
    str(notebook_dir),
]

import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from dual_feg_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

certificate_path = (
    "supplementary/n8/dual_feg_b2.json"
    if len(sys.argv) > 1 and sys.argv[1] == "8"
    else "state/dual_feg_b2.json"
)
certificate = json.loads((notebook_dir / certificate_path).read_text())
N_int = certificate["N_verify"]
params_sp = {"L": sp.S.One, "R": sp.S.One}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
for filename in ("b3_certificate_check.py", "b3_decomposition.py", "b3_grouping.py"):
    exec(
        compile(
            (notebook_dir / "supplementary" / filename).read_text(), filename, "exec"
        )
    )
observation = {
    "N": N_int,
    "certificate_id": certificate["certificate_id"],
    "recipe_id": "terminal-star-step-pairs-S-boundary",
    "rank_profile": ranks,
    "singular_values": singular_values,
    "rank_convention": {
        "absolute_tolerance": 1e-4,
        "scaling": "none; L=R=1",
        "coordinate_order": "setup basis order",
    },
    "certificate_checked": certificate_checked,
    "grouping_checked": grouping_checked,
    "rank_credible": all(
        not any(0.5e-4 < s < 2e-4 for s in row) for row in singular_values
    ),
    "coverage_max_abs": max(coverage_residuals),
    "boundary_exclusions": {"left": rank_left, "right": rank_right},
    "certificate_path": certificate_path,
}
(notebook_dir / f"supplementary/b3-rank-N{N_int}.json").write_text(
    json.dumps(observation, indent=2)
)
print("Rank credibility:", observation["rank_credible"])
