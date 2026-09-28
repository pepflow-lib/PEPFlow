from pathlib import Path
import json
root=Path.cwd()
data=json.loads((root/"supplementary/samples/N6/bppm_b2.json").read_text())
assert data["numerical_checks"]["passed"]
record={"current_block":"B2","completion_status":"complete_additional_horizon","next_block":"B3",
"entry_exit_reason":"Acquired and verified coherent dense/sparse N=6 certificate under unchanged solver policy and sparsity recipe. N=4 remains selected.",
"operational_status":"awaiting_same_session_continuation","sample":"samples/N6/bppm_b2.json","certificate_id":data["certificate_id"],
"checks":data["numerical_checks"],"source_changes":False,"notebook_status":"Selected N=4 notebook retained; N=6 comparison belongs to resumed B3.",
"consulted_sources":"Own selected certificate, setup, helpers; fingerprinted approved sources for hashes only.",
"access_control":"instruction_only","prohibited_content_observed":False,"remaining_work":"B3 cross-horizon comparison and notebook/state completion, then B4-B5."}
(root/"supplementary/b2-N6-handoff.json").write_text(json.dumps(record,indent=2))
print("N=6 certificate acquired and checked; stopped before B3 comparison.")
