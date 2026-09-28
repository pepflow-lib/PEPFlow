# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
exec(
    compile(
        (ROOT / "supplementary" / "run_b1.py").read_text().split("results = []")[0],
        "bootstrap",
        "exec",
    )
)
setup = importlib.import_module("pgm_setup")
notebook_dir = ROOT
get_pep_setup = setup.get_pep_setup
horizon = int(sys.argv[1]) if len(sys.argv) > 1 else 4
certificate_path = (
    ROOT / "state" / "pgm_b2.json"
    if horizon == 4
    else ROOT / "supplementary" / f"N{horizon}" / "pgm_b2.json"
)
certificate = json.loads(certificate_path.read_text())
source = (ROOT / "supplementary" / "b3_construct.py").read_text()
exec(compile(source, str(ROOT / "supplementary" / "b3_construct.py"), "exec"))
observation = dict(
    N=N_int,
    certificate_id=certificate["certificate_id"],
    recipe_id="star_and_consecutive_by_destination_minus_polar_aligned_supplied_sos",
    rank_profile=ranks,
    singular_values=singular_values,
    rank_credible=rank_credible,
    certificate_checked=certificate_checked,
    grouping_checked=grouping_checked,
    rank_convention=dict(
        tolerance=1e-4,
        scaling="unscaled Gram matrix",
        coordinate_order="setup insertion order",
    ),
    coverage_residuals=coverage_residuals,
    certificate_residuals=certificate_residuals,
    increment_residuals=increment_residuals,
    piece_residuals=piece_residuals,
    term_assignment=term_assignment,
    S_assignment=S_assignment,
    boundary_constraints=[],
    boundary_S=[],
    omitted_constraints=[],
    source=source,
    decomposition_trial=decomposition_trial,
)
(ROOT / "supplementary" / f"b3-rank-N{N_int}.json").write_text(
    json.dumps(observation, indent=2)
)
