"""Fresh replay of the exact saved B3 and B4 mathematical source fields."""

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
sys.path[:0] = [
    str(ROOT / "supplementary" / "approved"),
    str(ROOT),
    str(ROOT / "supplementary" / "helpers"),
]
import numpy as np  # noqa: E402

import pepflow as pf  # noqa: E402

state = json.loads((ROOT / "state" / "ogm_b4.json").read_text())
ns: dict[str, Any] = dict(certificate=state, notebook_dir=ROOT, np=np, pf=pf)
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(compile(state[field], field, "exec"), ns)
ctx, pb, obj, pm, terms, checks = ns["check_certificate"](state, ROOT)
ns.update(
    ctx=ctx,
    pb=pb,
    obj=obj,
    pm=pm,
    coeff_by_k={
        int(k): np.asarray(v, dtype=float).reshape((len(v), len(v)))
        for k, v in state["coeff_by_k"].items()
    },
)
exec(compile(state["basis_code"], "basis_code", "exec"), ns)
exec(compile(state["structure_code"], "structure_code", "exec"), ns)
lyap = [pf.Scalar.zero()]
for k in range(state["N"]):
    lyap.append(
        lyap[-1]
        + sum(
            (
                terms[name]
                for name, step in state["grouping_coverage"][
                    "constraint_assignment"
                ].items()
                if step == k
            ),
            pf.Scalar.zero(),
        )
    )
errors = []
for k, V in enumerate(lyap):
    evaluated = pm.eval_scalar(ns["V_k_structure"](k) - V)
    error = max(
        float(np.max(np.abs(np.asarray(c, dtype=float)), initial=0))
        for c in (
            evaluated.inner_prod_coords,
            evaluated.func_coords,
            np.asarray(evaluated.offset),
        )
    )
    assert error <= 1e-4
    errors.append(error)
(ROOT / "supplementary" / "b4-source-replay.json").write_text(
    json.dumps(
        dict(
            passed=True,
            all_index_errors=errors,
            source_fields=[
                "certificate_check_code",
                "decomposition_code",
                "grouping_code",
                "basis_code",
                "structure_code",
            ],
        ),
        indent=2,
    )
)
print("Exact saved-source replay passed:", errors)
