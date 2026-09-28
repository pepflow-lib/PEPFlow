"""Rebuild selected partial sums and execute candidate search and extraction."""

import contextlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for key in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]:
    os.environ[key] = "1"
sys.path[:0] = [
    str(ROOT / "supplementary/approved"),
    str(ROOT),
    str(ROOT / "supplementary"),
]
import numpy as np  # noqa: E402
from b4_notebook_cells import (  # noqa: E402 - imports follow runtime or notebook setup
    BASIS,
    EXTRACT,
    FILTER,
    FIT,
    SANITY,
    SCAN,
    SEARCH,
)
from ogm_setup import L, get_pep_setup, theta_sequence  # noqa: E402

import pepflow as pf  # noqa: E402

b3 = json.loads((ROOT / "state/ogm_b3.json").read_text())
ns: dict[str, Any] = dict(
    notebook_dir=ROOT,
    json=json,
    np=np,
    pf=pf,
    L=L,
    get_pep_setup=get_pep_setup,
    theta_sequence=theta_sequence,
)
with (
    (ROOT / "supplementary/b4-recheck-output.txt").open("w") as stream,
    contextlib.redirect_stdout(stream),
):
    for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
        exec(b3[field], ns)
for source in (SANITY, SCAN, FILTER, SEARCH, BASIS, EXTRACT, FIT):
    exec(source, ns)
structure_function = EXTRACT[
    EXTRACT.index("def V_k_structure(k):") : EXTRACT.index(
        "for k in range(N+1):", EXTRACT.index("def V_k_structure(k):")
    )
]
structure_code = "alpha_by_k = " + repr(ns["alpha_by_k"]) + "\n" + structure_function
exec(structure_code, ns)
for k in range(b3["N_verify"] + 1):
    replayed = ns["pm"].eval_scalar(ns["V_k_structure"](k) - ns["lyap"][k])
    assert all(
        float(np.max(np.abs(np.asarray(coords, dtype=float)), initial=0)) <= 1e-4
        for coords in (
            replayed.inner_prod_coords,
            replayed.func_coords,
            replayed.offset,
        )
    )
data = dict(
    coeff_by_k={str(k): v.tolist() for k, v in ns["coeff_by_k"].items()},
    alpha_by_k=ns["alpha_by_k"],
    quadratic_residuals=ns["coefficient_residuals"],
    component_residuals=ns["component_residuals"],
    formula_residuals=ns["formula_residuals"],
    searched_basis={
        str(k): [ns["candidate_labels"][id(v)] for v in vectors]
        for k, vectors in ns["searched_basis"].items()
    },
    column_space_candidates={
        str(k): [ns["candidate_labels"][id(v)] for v in vectors]
        for k, vectors in ns["spanning_by_k"].items()
    },
)
(ROOT / "supplementary/b4-exploration.json").write_text(
    json.dumps(data, indent=2, allow_nan=False)
)
print("Extracted coefficient matrices:", json.dumps(data["coeff_by_k"]))
