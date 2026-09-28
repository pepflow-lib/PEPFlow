import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import configure,NOTEBOOK_DIR
configure()
import inspect
import json
import numpy as np
from grouping import replay
from transport_grouping import construct,transport_pieces

samples=[]
selected=json.loads((NOTEBOOK_DIR/"state/pgm_b2.json").read_text())
for path in [NOTEBOOK_DIR/"supplementary/N6-selected/pgm_b2.json",NOTEBOOK_DIR/"state/pgm_b2.json"]:
    cert=json.loads(path.read_text())
    ctx,pb,lyap,sample=construct(cert)
    samples.append(sample)
    (NOTEBOOK_DIR/f"supplementary/b3-N{cert['N_verify']}-verified.json").write_text(json.dumps(sample,indent=2))
    print("N",cert["N_verify"],"rank credible",sample["rank_credible"],
          "coverage",sample["coverage_residual"])
left,right=1,1
assert len({s["N"] for s in samples})>=2
assert all(s["recipe_id"]==samples[0]["recipe_id"] for s in samples)
assert all(s["rank_convention"]==samples[0]["rank_convention"] for s in samples)
assert all(s["rank_credible"] and s["certificate_checked"] and s["grouping_checked"] for s in samples)
retained=[s["rank_profile"][left:s["N"]+1-right] for s in samples]
assert all(len(r)>=3 for r in retained)
assert len({rank for r in retained for rank in r})==1
summary=dict(status="confirmed",boundary_exclusions={"left":left,"right":right},
    rank=retained[0][0],confirmed_horizons=[s["N"] for s in samples],
    selected_certificate_id=selected["certificate_id"],recipe_id=samples[0]["recipe_id"],
    rank_convention=samples[0]["rank_convention"],unresolved_samples=[],
    evidence_path="supplementary/rank_search.json")
(NOTEBOOK_DIR/"supplementary/rank_search.json").write_text(json.dumps({"summary":summary,"samples":samples},indent=2))
sample=samples[-1]
checks_source=inspect.getsource(replay)
group_source=inspect.getsource(construct)
state={**selected,"rank_profile":sample["rank_profile"],"rank_search":summary,
"lyap_inner_prod_coords":[c["gram"] for c in sample["coordinates"]],
"lyap_func_coords":[c["func"] for c in sample["coordinates"]],
"lyap_offsets":[c["offset"] for c in sample["coordinates"]],
"certificate_check_code":checks_source+"\nctx, pb, certificate_checks = replay(certificate)\ncertificate_checked = True\n",
"decomposition_code":inspect.getsource(transport_pieces),
"grouping_code":group_source+"\nctx, pb, lyap, observation = construct(certificate)\ngrouping_checked = observation['grouping_checked']\n",
"extra_duals":{},"rank_tolerance":1e-4,"reconstruction_tolerance":1e-4,
"reconstruction_rtol":1e-5,
"grouping_coverage":{"constraint_assignment":sample["constraint_assignment"],
"S_assignment":sample["S_assignment"],"normalization_constraint":"initial_condition",
"boundary_constraints":[],"boundary_S":[],"omitted_constraints":[],"checked":True,
"coverage_residual":sample["coverage_residual"],"step_residuals":sample["step_residuals"]},
"grouping_source_file":"supplementary/helpers/transport_grouping.py",
"numerical_certificate_verified":True,"analytic_full_pep_verified":False,
"lyapunov_proof_verified":False}
assert np.isfinite(np.array(state["lyap_inner_prod_coords"])).all()
(NOTEBOOK_DIR/"state/pgm_b3.json").write_text(json.dumps(state,indent=2))
print("Confirmed:",summary)

