# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Replay and search meaningful vector bases for every selected partial sum."""

import hashlib  # noqa: F401 -- Required by exec of dual_feg_b3.json#certificate_check_code.
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "supplementary"), str(ROOT / "supplementary/helpers")]
import numpy as np  # noqa: E402
import run_b1  # noqa: E402,F401

import pepflow as pf  # noqa: E402, F401 -- Required by exec of dual_feg_b3.json#certificate_check_code. Paths initialized above.
from pepflow.lyapunov_utils import (  # noqa: E402 - imports follow runtime or notebook setup
    find_basis_with_sparsest_coefficients,
    find_symmetric_coefficient_matrix,
    vectors_in_column_space,
)

# Preserve the recorded import initialization order.
# isort: split
from dual_feg_setup import (  # noqa: E402, F401 -- Required by exec of dual_feg_b3.json#certificate_check_code. Paths initialized above.
    get_pep_setup,
)

b3 = json.loads((ROOT / "state/dual_feg_b3.json").read_text())
certificate = b3
notebook_dir = ROOT
dense_value = json.loads((ROOT / "state/dual_feg_dense.json").read_text())["opt_value"]
for field in ["certificate_check_code", "decomposition_code", "grouping_code"]:
    exec(compile(b3[field], field, "exec"), globals())
assert certificate_checked and grouping_checked
n = b3["N_verify"]
assert observation["rank_profile"] == b3["rank_profile"]
evidence = json.loads((ROOT / b3["rank_search"]["evidence_path"]).read_text())
assert evidence["summary"] == b3["rank_search"]
for k, value in enumerate(lyap):
    evaluated = pm.eval_scalar(value)
    assert np.allclose(
        np.asarray(evaluated.inner_prod_coords, dtype=float),
        b3["lyap_inner_prod_coords"][k],
        atol=1e-4,
        rtol=1e-5,
    )
    assert np.allclose(
        evaluated.func_coords, b3["lyap_func_coords"][k], atol=1e-4, rtol=1e-5
    )
    assert np.allclose(
        float(evaluated.offset), b3["lyap_offsets"][k], atol=1e-4, rtol=1e-5
    )
pairs = []
for tag in [f"g_{n}"] + [f"z_{k}" for k in range(1, n + 1)]:
    pairs.append((tag, ctx[tag]))
for k in range(n):
    pairs.append((f"x_{k}-x_N", ctx[f"x_{k}"] - ctx[f"x_{n}"]))
for tag in (
    ["x_star"] + [f"x_{k}" for k in range(n + 1)] + [f"x_half_{k}" for k in range(n)]
):
    pairs.append((tag, ctx[tag]))
for v in ctx.basis_vectors():
    pairs.append((str(v), v))
point_tags = [f"x_{k}" for k in range(n + 1)] + ["x_star"]
for a, b in itertools.combinations(point_tags, 2):
    pairs.append((f"{a}-{b}", ctx[a] - ctx[b]))
unique, coords_seen = [], []
for label, vector in pairs:
    coordinate = np.asarray(pm.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(coordinate) <= 1e-12 or any(
        np.allclose(coordinate, prev, atol=1e-12, rtol=0) for prev in coords_seen
    ):
        continue
    unique.append((label, vector))
    coords_seen.append(coordinate)
labels = {id(v): label for label, v in unique}
params = json.loads(b3["params_json"])
results = {}
for k in range(n + 1):
    in_col = vectors_in_column_space(
        lyap[k],
        [v for _, v in unique],
        pep_context=ctx,
        resolve_parameters=params,
        rtol=1e-4,
        atol=1e-4,
    )
    print("k", k, "in_col", [labels[id(v)] for v in in_col], flush=True)
    basis, C = find_basis_with_sparsest_coefficients(
        lyap[k],
        in_col,
        pep_context=ctx,
        resolve_parameters=params,
        zero_tol=1e-6,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    print(
        "sparse basis",
        [labels[id(v)] for v in basis],
        "zero coefficients",
        int(np.sum(abs(C) < 1e-6)),
        "/",
        C.size,
        flush=True,
    )
    adopted = (
        []
        if k == 0
        else [ctx[f"g_{n}"], ctx["x_0"] - ctx[f"x_{n}"]]
        if k == n
        else [
            ctx[f"g_{n}"],
            ctx["x_0"] - ctx[f"x_{n}"],
            ctx[f"x_{k}"] - ctx[f"x_{n}"],
            ctx[f"z_{k}"],
        ]
    )
    try:
        adopted_C = find_symmetric_coefficient_matrix(
            lyap[k],
            adopted,
            pep_context=ctx,
            resolve_parameters=params,
            indep_tol=1e-7,
            span_tol=1e-5,
        )
        print("adopted coefficient", adopted_C, flush=True)
        adoption_error = None
    except ValueError as exc:
        adopted_C, adoption_error = np.empty((0, 0)), str(exc)
        print("adoption failed", adoption_error, flush=True)
    results[str(k)] = dict(
        in_column_labels=[labels[id(v)] for v in in_col],
        sparse_basis=[labels[id(v)] for v in basis],
        sparse_coefficients=C.tolist(),
        adopted_coefficients=adopted_C.tolist(),
        adoption_error=adoption_error,
    )
(ROOT / "supplementary/b4-discovery.json").write_text(json.dumps(results, indent=2))
