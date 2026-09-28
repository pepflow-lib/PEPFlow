# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json
from itertools import combinations

import numpy as np
import runtime

from pepflow.lyapunov_utils import (
    find_basis_with_sparsest_coefficients,
    vectors_in_column_space,
)

root = runtime.ATTEMPT
b3 = json.loads((root / "state/pgm_b3.json").read_text())
certificate = b3
for key in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(compile(b3[key], key, "exec"))
ctx = ctx_b2
params_sp = {"L": sp.S.One, "R": sp.S.One}
base = [(str(v), v) for v in ctx.basis_vectors()]
base += [(f"x_{j}", ctx[f"x_{j}"]) for j in range(N + 1)]
base += [
    (f"a_{j}-a_star", f.grad(ctx[f"x_{j}"]) - f.grad(ctx["x_star"]))
    for j in range(N + 1)
]
base += [
    (f"s_{j}+a_star", g.grad(ctx[f"x_{j}"]) + f.grad(ctx["x_star"]))
    for j in range(1, N + 1)
]
base += [
    (f"a_{j}+s_{j}", f.grad(ctx[f"x_{j}"]) + g.grad(ctx[f"x_{j}"]))
    for j in range(1, N + 1)
]
base += [(f"x_{j}-x_star", ctx[f"x_{j}"] - ctx["x_star"]) for j in range(N + 1)]
raw = base + [
    (f"({base[i][0]})-({base[j][0]})", base[i][1] - base[j][1])
    for i, j in combinations(range(len(base)), 2)
]
candidate_pairs = []
seen = []
for label, v in raw:
    coords = np.asarray(pm.eval_vector(v).coords, dtype=float)
    if np.linalg.norm(coords) < 1e-10:
        continue
    if any(np.array_equal(coords, old) or np.array_equal(coords, -old) for old in seen):
        continue
    seen.append(coords)
    candidate_pairs.append((label, v))
labels = {id(v): label for label, v in candidate_pairs}
observations = {}
for k in range(1, N + 1):
    in_col = vectors_in_column_space(
        lyap[k],
        [v for _, v in candidate_pairs],
        pep_context=ctx,
        resolve_parameters=params_sp,
        atol=1e-4,
        rtol=1e-4,
    )
    print("k", k, "candidates", [labels[id(v)] for v in in_col], flush=True)
    basis, C = find_basis_with_sparsest_coefficients(
        lyap[k],
        in_col,
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=1e-6,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    print("basis", [labels[id(v)] for v in basis], "C", C, flush=True)
    observations[k] = dict(
        candidates=[labels[id(v)] for v in in_col],
        basis=[labels[id(v)] for v in basis],
        C=C.tolist(),
    )
(root / "supplementary/b4-scan-002.json").write_text(json.dumps(observations, indent=2))
