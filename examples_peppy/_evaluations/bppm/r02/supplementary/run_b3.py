from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import ATTEMPT
from partial_sums import replay_certificate,construct_partial_sums
from bppm_setup import get_pep_setup
import json

certificate=json.loads((ATTEMPT/"state/bppm_b2.json").read_text())
ctx,pb,obj=get_pep_setup(certificate["N_verify"],{})
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
checks=replay_certificate(ctx,pb,certificate,ATTEMPT)
lyap,observation=construct_partial_sums(ctx,pb,certificate)
(ATTEMPT/"supplementary/b3-N4-observation.json").write_text(json.dumps(observation,indent=2))
print("Full-coordinate grouping checks:",observation["coordinate_errors"])
print("Minimum significant singular value:",observation["minimum_significant_singular_value"])
print("Maximum negligible singular value:",observation["maximum_negligible_singular_value"])
