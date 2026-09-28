import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b2_acquire as acquisition

acquisition.N = 6
dense6 = acquisition.acquire([], "supplementary/b2-N6-dense.json")
points6 = ["z_0"] + [f"x_{k}" for k in range(1, 7)]
keep6 = (
    {f"f:x_star,{p}" for p in points6}
    | {f"f:{a},{b}" for a, b in zip(points6[:-1], points6[1:])}
    | {"initial_condition"}
)
relaxed6 = [name for name in dense6["named_dual_values"] if name not in keep6]
acquisition.acquire(relaxed6, "supplementary/b2-N6-chain-certificate.json")
notebook_dir = acquisition.attempt
from ogm_setup import (  # noqa: E402, F401 -- Required by exec of b2_notebook_cells.py. Paths initialized above.
    get_pep_setup,
    theta_sequence,
)

# Preserve the recorded import initialization order.
# isort: split
import json  # noqa: E402, F401 -- Required by exec of b2_notebook_cells.py. Paths initialized above.

import pepflow as pf  # noqa: E402, F401 -- Required by exec of b2_notebook_cells.py. Paths initialized above.

source = (notebook_dir / "supplementary/b2_notebook_cells.py").read_text()
source = source.replace("state/ogm_dense.json", "supplementary/b2-N6-dense.json")
source = source.replace(
    "supplementary/b2-chain-certificate.json",
    "supplementary/b2-N6-chain-certificate.json",
)
source = source.replace("assert N == b1['N_verify']", "assert N == 6")
source = source.replace(
    "for name in ('ogm_b2.json','ogm_relaxed.json'):",
    "for name in ('b2-N6-verified.json',):",
)
source = source.replace(
    "(notebook_dir/'state'/name)", "(notebook_dir/'supplementary'/name)"
)
(notebook_dir / "supplementary/b2_N6_verified_source.py").write_text(source)
exec(compile(source, "b2_N6_verified_source.py", "exec"))
