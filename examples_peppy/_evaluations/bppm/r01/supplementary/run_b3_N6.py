# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import runtime
import sympy as sp
from bppm_setup import get_pep_setup

REPO_ROOT = runtime.APPROVED
SOURCE_ROOT = runtime.ROOT
certificate = json.loads(
    (SOURCE_ROOT / "supplementary/N6/certificate.json").read_text()
)
N_int = certificate["N_verify"]
params_sp = {"alpha": sp.S(1), "R": sp.S(1)}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
ctx.set_as_current()
for file in (
    "b3_certificate_check.py",
    "b3_decomposition.py",
    "b3_grouping.py",
    "b3_coverage.py",
):
    source = (SOURCE_ROOT / "supplementary" / file).read_text(encoding="utf-8-sig")
    exec(compile(source, file, "exec"))
observation = dict(
    N=N_int,
    certificate_id=certificate["certificate_id"],
    recipe_id="consecutive_all_owners_terminal_h_and_full_S_boundary",
    rank_profile=ranks,
    rank_convention=dict(
        tolerance=rank_tolerance,
        scaling="none; absolute singular-value threshold",
        coordinate_order="PEPContext basis order",
    ),
    rank_credible=rank_credible,
    certificate_checked=certificate_checked,
    grouping_checked=grouping_checked,
    singular_values=singular_values,
    boundary_exclusions=dict(left=1, right=1),
    boundary_names=boundary_names,
    boundary_S=boundary_S,
)
(SOURCE_ROOT / "supplementary/b3-observation-N6.json").write_text(
    json.dumps(observation, indent=2)
)
print("Observation preserved; cross-horizon confirmation pending.")
