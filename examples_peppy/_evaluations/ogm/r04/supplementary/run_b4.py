import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import configure  # ty: ignore[unresolved-import]

notebook_dir, REPO_ROOT = configure()
import json  # noqa: E402 - imports follow runtime or notebook setup

import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from ogm_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

# Preserve the recorded order of setup bindings used by exec.
# isort: split
from ogm_setup import (  # noqa: E402, F401 -- Required by exec of ogm_b3.json#certificate_check_code. Paths initialized above.
    theta_sequence,
)

certificate = json.loads((notebook_dir / "state/ogm_b3.json").read_text())
N_int = certificate["N_verify"]
params_sp = {k: sp.S(v) for k, v in json.loads(certificate["params_json"]).items()}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(compile(certificate[field], field, "exec"))
source = (notebook_dir / "supplementary/b4_cells.py").read_text(encoding="utf-8-sig")
exec(compile(source, "b4_cells.py", "exec"))
