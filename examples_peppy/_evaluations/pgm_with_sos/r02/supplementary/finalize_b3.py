import importlib.util
import inspect
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
import aligned_sos  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
import candidates  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
import certificate  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
import partial_sums  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup

samples = []
trials = []
for source in ("state/pgm_b2.json", "supplementary/b2-n6-certificate.json"):
    state = json.loads((root / source).read_text())
    trial = partial_sums.construct(state, variant="blend-3/10")
    observation = trial["observation"]
    observation["certificate_path"] = source
    samples.append(observation)
    trials.append(trial)
    (root / f"supplementary/b3-n{state['N']}-blend-replay.json").write_text(
        json.dumps(observation, indent=2)
    )
    print(
        "N",
        state["N"],
        "ranks",
        observation["rank_profile"],
        "credible",
        observation["rank_credible"],
        "checks",
        observation["checks"],
    )
left = right = 1
retained = [
    sample["rank_profile"][left : sample["N"] + 1 - right] for sample in samples
]
confirmed = (
    all(len(r) >= 3 and len(set(r)) == 1 for r in retained)
    and len(set(r[0] for r in retained)) == 1
    and all(s["rank_credible"] for s in samples)
)
assert confirmed
b2 = json.loads((root / "state/pgm_b2.json").read_text())
trial = trials[0]
summary = dict(
    status="confirmed",
    boundary_exclusions=dict(left=left, right=right),
    rank=retained[0][0],
    confirmed_horizons=[s["N"] for s in samples],
    selected_certificate_id=b2["certificate_id"],
    recipe_id="blend-3/10",
    rank_convention=samples[0]["rank_convention"],
    unresolved_samples=[],
    evidence_path="supplementary/rank_search.json",
)
(root / "supplementary/rank_search.json").write_text(
    json.dumps(dict(summary=summary, samples=samples), indent=2)
)
values = [trial["pm"].eval_scalar(v) for v in trial["lyap"]]
b3 = {
    **b2,
    "rank_profile": samples[0]["rank_profile"],
    "rank_search": summary,
    "lyap_inner_prod_coords": [
        np.asarray(v.inner_prod_coords, dtype=float).tolist() for v in values
    ],
    "lyap_func_coords": [
        np.asarray(v.func_coords, dtype=float).tolist() for v in values
    ],
    "lyap_offsets": [float(v.offset) for v in values],
    "certificate_check_code": inspect.getsource(certificate.inventory)
    + "\n"
    + inspect.getsource(certificate.residual_of)
    + "\n"
    + inspect.getsource(certificate.verify)
    + "\n"
    + inspect.getsource(partial_sums.replay),
    "decomposition_code": inspect.getsource(candidates.sos_pieces)
    + "\n"
    + inspect.getsource(aligned_sos.aligned_squares),
    "grouping_code": inspect.getsource(partial_sums.construct),
    "replay_dependencies": {
        "CERTIFICATE_KEYS": list(partial_sums.CERTIFICATE_KEYS),
        "ROOT": "notebook_dir",
        "APPROVED": "notebook_dir/supplementary/approved",
        "TOL": certificate.TOL,
    },
    "extra_duals": {},
    "rank_tolerance": 1e-4,
    "reconstruction_tolerance": 1e-4,
    "reconstruction_rtol": 1e-5,
    "grouping_coverage": dict(
        constraint_assignment=trial["term_assignment"],
        S_assignment=trial["S_assignment"],
        normalization_constraint="initial_condition",
        boundary_constraints=[],
        boundary_S=[],
        omitted_constraints=[],
        checked=True,
        checks=samples[0]["checks"],
    ),
    "sign_convention": "Every increment is a sum of nonnegative multipliers times interpolation residuals <=0, minus nonnegative square pieces; V_{k+1} <= V_k. V_0=0; normalization handled at final boundary.",
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(root / "state/pgm_b3.json").write_text(json.dumps(b3, indent=2))
print("Cross-horizon rank confirmation", summary)
