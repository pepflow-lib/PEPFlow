# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import numpy as np
import pgm_setup as mod

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

from pepflow.lyapunov_utils import (
    find_basis_with_sparsest_coefficients,
    vectors_in_column_space,
)

REPO_ROOT = runtime.ROOT
b3 = json.loads((REPO_ROOT / "state/pgm_b3.json").read_text())
certificate = b3
N_int = b3["N_verify"]
params_sp = json.loads(b3["params_json"])
ctx, pb, obj = mod.get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(b3["relaxed_constraints"])
f, g = mod.f, mod.g
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(b3[field])
base = [("x0-star", ctx["x_0"] - ctx["x_star"])]
for i in range(N_int + 1):
    base += [
        (f"x{i}-star", ctx[f"x_{i}"] - ctx["x_star"]),
        (f"a{i}-astar", f.grad(ctx[f"x_{i}"]) - f.grad(ctx["x_star"])),
    ]
    if i:
        base += [
            (f"hgrad{i}", f.grad(ctx[f"x_{i}"]) + g.grad(ctx[f"x_{i}"])),
            (f"proxstep{i}", ctx[f"x_{i - 1}"] - ctx[f"x_{i}"]),
        ]
base += [(str(v), v) for v in ctx.basis_vectors()]
for k in range(1, N_int + 1):
    pairs = []
    coords = []
    for label, v in base:
        a = np.asarray(pm.eval_vector(v).coords, dtype=float)
        if np.linalg.norm(a) < 1e-7 or any(
            np.allclose(a, b, atol=1e-7, rtol=0) for b in coords
        ):
            continue
        pairs.append((label, v))
        coords.append(a)
    included = vectors_in_column_space(
        lyap[k],
        [v for _, v in pairs],
        pep_context=ctx,
        resolve_parameters=params_sp,
        atol=1e-4,
        rtol=1e-4,
    )
    labels = {id(v): label for label, v in pairs}
    print("k", k, "candidates", [labels[id(v)] for v in included], flush=True)
    try:
        bs, C = find_basis_with_sparsest_coefficients(
            lyap[k],
            included,
            pep_context=ctx,
            resolve_parameters=params_sp,
            zero_tol=1e-6,
            indep_tol=1e-7,
            span_tol=1e-5,
        )
        print("basis", [labels[id(v)] for v in bs], "C", C, flush=True)
        B = np.column_stack([pm.eval_vector(v).coords for v in bs]).astype(float)
        print(
            "Frobenius residual",
            np.linalg.norm(
                B @ C @ B.T - pm.eval_scalar(lyap[k]).inner_prod_coords.astype(float)
            ),
            flush=True,
        )
    except ValueError as error:
        print("FAILED", repr(error), flush=True)
