# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import importlib.util
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime", root / "supplementary/helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import dual_feg_setup as setup  # noqa: E402 - imports follow runtime or notebook setup
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup

notebook_dir = root
REPO_ROOT = runtime.REPO_ROOT
certificate_path = root / (
    sys.argv[1] if len(sys.argv) > 1 else "state/dual_feg_b2.json"
)
certificate = json.loads(certificate_path.read_text())
N_int = certificate["N_verify"]
N = sp.Integer(N_int)
params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.Integer(1), "R": sp.Integer(1)}
ctx, pb, obj = setup.get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
for name in ["b3_certificate_check.py", "b3_decomposition.py", "b3_grouping.py"]:
    exec((root / "supplementary" / name).read_text(encoding="utf-8-sig"))
record = {
    "N": N_int,
    "certificate_id": certificate["certificate_id"],
    "recipe_id": "forward_step_terminal_monotonicity_whole_S_boundary",
    "rank_profile": ranks,
    "singular_values": singular_values,
    "rank_convention": {
        "tolerance": 1e-4,
        "scaling": "none; absolute singular values",
        "coordinate_order": "original earlier-iterates-first",
    },
    "certificate_checked": certificate_checked,
    "grouping_checked": grouping_checked,
    "coverage_residuals": coverage_residuals,
}
(root / f"supplementary/b3-rank-N{N_int}.json").write_text(json.dumps(record, indent=2))

record["rank_credible"] = all(
    all(v > 1e-3 or v < 1e-5 for v in sv) for sv in singular_values
)
record["certificate_path"] = str(certificate_path.relative_to(root)).replace(
    chr(92), "/"
)
(root / f"supplementary/b3-rank-N{N_int}.json").write_text(json.dumps(record, indent=2))
