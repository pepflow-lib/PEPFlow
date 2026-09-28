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
import pgm_setup as setup  # noqa: E402 - imports follow runtime or notebook setup
from partial_sums import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    construct,
)
from scipy.optimize import (  # noqa: E402 - imports follow runtime or notebook setup
    minimize_scalar,
)

record = []
for source in ("state/pgm_b2.json", "supplementary/b2-n6-certificate.json"):
    data = json.loads((root / source).read_text())
    canon = construct(data, "canonical")
    polar = construct(data, "polar-aligned")
    ctx = polar["ctx"]
    pm = polar["pm"]
    n = data["N"]
    canonical_matrices = [
        np.asarray(canon["pm"].eval_scalar(v).inner_prod_coords, dtype=float)
        for v in canon["lyap"]
    ]
    polar_matrices = [
        np.asarray(pm.eval_scalar(v).inner_prod_coords, dtype=float)
        for v in polar["lyap"]
    ]
    projectors = []
    for k in range(n + 1):
        if k == 0:
            projectors.append(np.zeros_like(canonical_matrices[0]))
            continue
        vectors = [ctx["x_0"] - ctx["x_star"]]
        if k < n:
            vectors += [
                ctx[f"x_{k}"] - ctx["x_star"],
                setup.f.grad(ctx[f"x_{k}"]),
                setup.f.grad(ctx[f"x_{k}"]) - setup.f.grad(ctx["x_star"]),
            ]
        B = np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
        projectors.append(B @ np.linalg.pinv(B))

    def errors(theta):
        matrices = [
            (1 - theta) * A + theta * B
            for A, B in zip(canonical_matrices, polar_matrices)
        ]
        return [
            float(np.linalg.norm(M - P @ M @ P, "fro"))
            for M, P in zip(matrices, projectors)
        ]

    opt = minimize_scalar(lambda t: max(errors(t)), bounds=(0, 1), method="bounded")
    result = dict(
        N=n,
        theta=float(opt.x),
        errors=errors(opt.x),
        canonical_errors=errors(0),
        polar_errors=errors(1),
        grid=[dict(theta=t, errors=errors(t)) for t in (0.1, 0.2, 0.3, 0.4, 0.5)],
    )
    record.append(result)
    print(json.dumps(result), flush=True)
(root / "supplementary/b3-blend-diagnostic.json").write_text(
    json.dumps(record, indent=2)
)
