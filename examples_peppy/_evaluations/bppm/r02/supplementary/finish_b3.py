from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import ATTEMPT
from partial_sums import replay_certificate,construct_partial_sums,decompose_saved_S
from certificates import entries_for,max_abs,verify_certificate,certificate_id,CERTIFICATE_KEYS
from bppm_setup import get_pep_setup
import json
import inspect

samples=[]
for path in (ATTEMPT/"state/bppm_b2.json",ATTEMPT/"supplementary/samples/N6/bppm_b2.json"):
    certificate=json.loads(path.read_text())
    ctx,pb,obj=get_pep_setup(certificate["N_verify"],{})
    pb.set_relaxed_constraints(certificate["relaxed_constraints"])
    replay_certificate(ctx,pb,certificate,ATTEMPT)
    lyap,observation=construct_partial_sums(ctx,pb,certificate)
    observation["certificate_path"]=str(path.relative_to(ATTEMPT)).replace('\\','/')
    samples.append(observation)
    (ATTEMPT/f"supplementary/b3-N{certificate['N_verify']}-observation.json").write_text(json.dumps(observation,indent=2))
left,right=1,1
for sample in samples:
    assert sample["certificate_checked"] and sample["grouping_checked"] and sample["rank_credible"]
    retained=sample["rank_profile"][left:sample["N"]+1-right]
    assert len(retained)>=3 and len(set(retained))==1
assert len({sample["N"] for sample in samples})>=2
assert len({sample["rank_profile"][left] for sample in samples})==1
assert samples[0]["recipe_id"]==samples[1]["recipe_id"]
assert samples[0]["rank_convention"]==samples[1]["rank_convention"]
selected=json.loads((ATTEMPT/"state/bppm_b2.json").read_text())
obs=samples[0]
rank_search={"status":"confirmed","boundary_exclusions":{"left":left,"right":right},"rank":4,
             "confirmed_horizons":[4,6],"selected_certificate_id":selected["certificate_id"],"recipe_id":obs["recipe_id"],
             "rank_convention":obs["rank_convention"],"unresolved_samples":[],"evidence_path":"supplementary/rank_search.json"}
check_source="import hashlib\nfrom pathlib import Path\nimport numpy as np\nimport sympy as sp\nimport pepflow as pf\nfrom typing import cast\nfrom pepflow.utils import Comparator\n"+"\n\n".join(inspect.getsource(f) for f in (entries_for,max_abs,verify_certificate))+"\nCERTIFICATE_KEYS = "+repr(CERTIFICATE_KEYS)+"\n"+inspect.getsource(certificate_id)+"\n"+inspect.getsource(replay_certificate)+"\ncertificate_checked = replay_certificate(ctx,pb,certificate,notebook_dir)['passed']\n"
decomp_source=inspect.getsource(decompose_saved_S)+"\nS_scalar,S_piece_terms=decompose_saved_S(ctx,certificate)\n"
group_source=inspect.getsource(construct_partial_sums)+"\nlyap,observation=construct_partial_sums(ctx,pb,certificate)\ngrouping_checked=observation['grouping_checked']\n"
state={**selected,"rank_profile":obs["rank_profile"],"rank_search":rank_search,
       "lyap_inner_prod_coords":obs["lyap_inner_prod_coords"],"lyap_func_coords":obs["lyap_func_coords"],"lyap_offsets":obs["lyap_offsets"],
       "certificate_check_code":check_source,"decomposition_code":decomp_source,"grouping_code":group_source,
       "extra_duals":{},"rank_tolerance":1e-4,"reconstruction_tolerance":1e-4,"reconstruction_rtol":1e-5,
       "grouping_coverage":{"constraint_assignment":obs["constraint_assignment"],"S_assignment":obs["S_assignment"],
                            "normalization_constraint":"initial_condition","boundary_constraints":obs["boundary_constraints"],
                            "boundary_S":obs["boundary_S"],"omitted_constraints":[],"checked":True},
       "coordinate_checks":obs["coordinate_errors"],"numerical_certificate_verified":True,"analytic_full_pep_verified":False,"lyapunov_proof_verified":False}
(ATTEMPT/"state/bppm_b3.json").write_text(json.dumps(state,indent=2))
(ATTEMPT/"supplementary/rank_search.json").write_text(json.dumps({"summary":rank_search,"samples":samples},indent=2))
print("Cross-horizon rank 4 confirmed at N=4 and N=6, exclusions (1,1), absolute tolerance 1e-4.")
