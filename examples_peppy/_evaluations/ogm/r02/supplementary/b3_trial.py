"""Recheck the selected certificate and observe a partial-sum rank recipe."""
import contextlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for key in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:
    os.environ[key] = "1"
sys.path[:0] = [str(ROOT / "supplementary/approved"), str(ROOT), str(ROOT / "supplementary")]
import numpy as np  # noqa: E402
import pepflow as pf  # noqa: E402
from ogm_setup import L, get_pep_setup, theta_sequence  # noqa: E402
from b2_notebook_cells import CANDIDATES, LOAD, VERIFY  # noqa: E402
from b3_notebook_cells import DECOMPOSITION, GROUPING  # noqa: E402

namespace: dict[str, Any] = dict(notebook_dir=ROOT, json=json, np=np, pf=pf,
                               get_pep_setup=get_pep_setup, theta_sequence=theta_sequence, L=L)
horizon = int(sys.argv[1]) if len(sys.argv) > 1 else 6
namespace["certificate_dir"] = ROOT / "state" if horizon == 6 else ROOT / "supplementary" / f"horizon_N{horizon}"
with (ROOT / "supplementary" / f"b3-certificate-recheck-N{horizon}.txt").open("w") as stream, contextlib.redirect_stdout(stream):
    exec(LOAD + "\n" + CANDIDATES + "\n" + VERIFY, namespace)
exec(DECOMPOSITION + "\n" + GROUPING, namespace)
sample = namespace["b2"]
evaluated_lyap = [namespace["pm"].eval_scalar(v) for v in namespace["lyap"]]
observation = dict(N=sample["N_verify"], certificate_id=sample["certificate_id"],
    recipe_id="star-prefix-forward-chain_whole-S-boundary", rank_profile=namespace["ranks"],
    singular_values=namespace["singular_values"], rank_convention=dict(tolerance=1e-4, scaling="absolute unscaled coordinate matrices", coordinate_order="initial point, optimum, chronological gradients"),
    certificate_checked=True, grouping_checked=namespace["grouping_checked"],
    rank_credible=all(not (1e-5 < s < 1e-3) for sv in namespace["singular_values"] for s in sv),
    constraint_assignment=namespace["term_assignment"], S_assignment=namespace["S_assignment"],
    coverage_checks=namespace["coverage_checks"], step_errors=namespace["step_errors"],
    boundary_exclusions=dict(left=1,right=1),
    certificate_check_code=LOAD + "\n" + CANDIDATES + "\n" + VERIFY,
    decomposition_code=DECOMPOSITION, grouping_code=GROUPING,
    lyap_inner_prod_coords=[np.asarray(v.inner_prod_coords, dtype=float).tolist() for v in evaluated_lyap],
    lyap_func_coords=[np.asarray(v.func_coords, dtype=float).tolist() for v in evaluated_lyap],
    lyap_offsets=[float(v.offset) for v in evaluated_lyap])
path = ROOT / "supplementary" / f'b3-rank-N{sample["N_verify"]}.json'
path.write_text(json.dumps(observation, indent=2, allow_nan=False))
print(json.dumps({"observation": str(path), "ranks": observation["rank_profile"],
                  "rank_credible": observation["rank_credible"], "singular_values": observation["singular_values"]}))
