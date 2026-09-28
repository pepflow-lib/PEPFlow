"""Recompute both saved samples with a single grouping recipe; no solves."""

import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "supplementary"), str(ROOT / "supplementary/helpers")]
import run_b1  # noqa: E402,F401

# local helper resolved by the notebook runtime path
from certificate import (  # noqa: E402  # ty: ignore[unresolved-import]
    certificate_id,
    inventory,
    verify_certificate,
)
from dual_feg_setup import get_pep_setup  # noqa: E402
from grouping import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    build_partial_sums,
    full_psd_piece,
    replay_certificate,
)

import pepflow as pf  # noqa: E402

samples = []
for cert_path, dense_path in [
    ("state/dual_feg_b2.json", "state/dual_feg_dense.json"),
    ("supplementary/b2-N6.json", "supplementary/b2-N6-dense.json"),
]:
    certificate = json.loads((ROOT / cert_path).read_text())
    dense = json.loads((ROOT / dense_path).read_text())
    checks, _, _ = replay_certificate(
        certificate, get_pep_setup, ROOT, dense["opt_value"]
    )
    ctx, pb, _ = get_pep_setup(
        certificate["N_verify"], json.loads(certificate["params_json"])
    )
    pm = pf.ExpressionManager(
        ctx, resolve_parameters=json.loads(certificate["params_json"])
    )
    S_scalar, S_piece_terms = full_psd_piece(certificate, ctx, pm)
    lyap, observation = build_partial_sums(
        certificate, ctx, pb, pm, S_scalar, S_piece_terms
    )
    observation["certificate_path"] = cert_path
    observation["dense_path"] = dense_path
    observation["certificate_replay_checks"] = checks
    samples.append(observation)
    (ROOT / f"supplementary/b3-rank-N{certificate['N_verify']}.json").write_text(
        json.dumps(observation, indent=2)
    )
left, right = 1, 1
assert len({s["N"] for s in samples}) == len(samples) >= 2
assert all(
    s["recipe_id"] == samples[0]["recipe_id"]
    and s["rank_convention"] == samples[0]["rank_convention"]
    for s in samples
)
retained = [s["rank_profile"][left : s["N"] + 1 - right] for s in samples]
assert all(len(r) >= 3 and len(set(r)) == 1 for r in retained)
assert len({r[0] for r in retained}) == 1
assert all(
    s["rank_credible"] and s["certificate_checked"] and s["grouping_checked"]
    for s in samples
)
selected = json.loads((ROOT / "state/dual_feg_b2.json").read_text())
summary = dict(
    status="confirmed",
    boundary_exclusions=dict(left=left, right=right),
    rank=retained[0][0],
    confirmed_horizons=[s["N"] for s in samples],
    selected_certificate_id=selected["certificate_id"],
    recipe_id=samples[0]["recipe_id"],
    rank_convention=samples[0]["rank_convention"],
    unresolved_samples=[],
    evidence_path="supplementary/rank_search.json",
)
(ROOT / "supplementary/rank_search.json").write_text(
    json.dumps(dict(summary=summary, samples=samples), indent=2)
)
obs = samples[0]
check_code = "\n".join(
    inspect.getsource(f)
    for f in [inventory, verify_certificate, certificate_id, replay_certificate]
)
check_code += '\nchecks, _, _ = replay_certificate(certificate, get_pep_setup, notebook_dir, dense_value)\nctx, pb, obj = get_pep_setup(certificate["N_verify"], json.loads(certificate["params_json"]))\npm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(certificate["params_json"]))\ncertificate_checked = checks["passed"]\n'
decomposition_code = (
    inspect.getsource(full_psd_piece)
    + "\nS_scalar, S_piece_terms = full_psd_piece(certificate, ctx, pm)\n"
)
grouping_code = (
    inspect.getsource(build_partial_sums)
    + '\nlyap, observation = build_partial_sums(certificate, ctx, pb, pm, S_scalar, S_piece_terms)\ngrouping_checked = observation["grouping_checked"]\n'
)
state = {
    **selected,
    **{
        k: obs[k]
        for k in [
            "rank_profile",
            "lyap_inner_prod_coords",
            "lyap_func_coords",
            "lyap_offsets",
            "grouping_coverage",
        ]
    },
    "rank_search": summary,
    "certificate_check_code": check_code,
    "decomposition_code": decomposition_code,
    "grouping_code": grouping_code,
    "extra_duals": {},
    "rank_tolerance": 1e-4,
    "reconstruction_tolerance": 1e-4,
    "reconstruction_rtol": 1e-5,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(ROOT / "state/dual_feg_b3.json").write_text(
    json.dumps(state, indent=2, allow_nan=False)
)
print("Cross-horizon rank confirmation:", summary)
