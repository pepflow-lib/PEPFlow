import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime", root / "supplementary/helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
from partial_sums import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    construct,
)

for source in ("state/pgm_b3.json", "supplementary/b2-n6-certificate.json"):
    data = json.loads((root / source).read_text())
    trial = construct(data)
    n = data["N"]
    pm = trial["pm"]
    prefix = sum(
        (
            np.asarray(pm.eval_scalar(p).inner_prod_coords, dtype=float)
            for name, p in trial["S_piece_terms"].items()
            if int(name.split("_")[1]) < n
        ),
        np.zeros_like(data["S_matrix"]),
    )
    last = np.asarray(data["S_matrix"]) - prefix
    print(
        "N",
        n,
        "terminal remainder eigenvalues",
        np.linalg.eigvalsh((last + last.T) / 2),
        flush=True,
    )
    np.savez(root / f"supplementary/b3-remainder-n{n}.npz", matrix=last, prefix=prefix)
