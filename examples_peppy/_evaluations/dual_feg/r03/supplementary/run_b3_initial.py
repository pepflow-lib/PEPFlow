"""Block 3 selected-sample grouping; does not acquire new certificates."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "supplementary"), str(ROOT / "supplementary/helpers")]
import run_b1  # noqa: E402,F401
from dual_feg_setup import get_pep_setup  # noqa: E402
from grouping import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    build_partial_sums,
    full_psd_piece,
    replay_certificate,
)

certificate = json.loads((ROOT / "state/dual_feg_b2.json").read_text())
dense = json.loads((ROOT / "state/dual_feg_dense.json").read_text())
checks, ctx, pm = replay_certificate(
    certificate, get_pep_setup, ROOT, dense["opt_value"]
)
_, pb, _ = get_pep_setup(
    certificate["N_verify"], json.loads(certificate["params_json"])
)
# Use the context returned by this second setup consistently, with its expression manager.
import pepflow as pf  # noqa: E402

ctx = pb.ctx
pm = pf.ExpressionManager(
    ctx, resolve_parameters=json.loads(certificate["params_json"])
)
S_scalar, S_piece_terms = full_psd_piece(certificate, ctx, pm)
lyap, observation = build_partial_sums(
    certificate, ctx, pb, pm, S_scalar, S_piece_terms
)
observation["certificate_replay_checks"] = checks
(ROOT / "supplementary/b3-rank-N4.json").write_text(json.dumps(observation, indent=2))
print("Rank credible:", observation["rank_credible"])
print("Coverage residuals:", observation["coverage_residuals"])
