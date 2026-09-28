from pathlib import Path
import json
import hashlib
root=Path.cwd()
assert json.loads((root/"supplementary/b4-static-002.json").read_text())["status"]=="passed"
nbpath=root/"bppm_example_lyap.ipynb"
nb=json.loads(nbpath.read_text())
for cell in nb["cells"]:
    if cell["cell_type"]=="code":
        assert cell["execution_count"] is not None
        assert not any(o["output_type"]=="error" for o in cell["outputs"])
search="".join("".join(o.get("text",[])) for o in nb["cells"][31]["outputs"])
assert all(f"k={k}: rank 4; sparse basis" in search for k in range(1,5))
assert sum(o["output_type"]=="display_data" for o in nb["cells"][35]["outputs"])==4
b4=json.loads((root/"state/bppm_b4.json").read_text())
max_error=max(v for row in b4["numerical_reconstruction"]["component_residuals"].values() for v in row.values())
path=root/"supplementary/bppm_example_lyap_checklist.md"
lines=path.read_text().replace("Last reviewed block: B3","Last reviewed block: B4").splitlines()
for i,line in enumerate(lines):
    if line.startswith("SHA-256:"):lines[i]="SHA-256: "+hashlib.sha256(nbpath.read_bytes()).hexdigest()
    if line.startswith("| 10 |"):
        p=line.split("|");p[3]=" verified ";p[4]=" 25-33 ";p[5]=" Candidate scan and actual sparse search at k=1..4; common rank-four basis independent; k=0 empty. ";lines[i]="|".join(p)
    if line.startswith("| 11 |"):
        p=line.split("|");p[4]=" 34-37 ";p[5]=" Numerical coefficient and full-expression reconstruction verified at k=0..4; candidate formula shown; exact closed form remains B5 pending. ";lines[i]="|".join(p)
    if line.startswith("| 12 |"):lines[i]=line.replace("| 27 |","| 38 |")
path.write_text("\n".join(lines)+"\n")
record={"current_block":"B4","completion_status":"complete","next_block":"B5","entry_exit_reason":"Interpretable basis and full-component reconstruction verified at every index; notebook/source checks passed.",
"operational_status":"awaiting_same_session_continuation","maximum_component_error":max_error,"numerical_certificate_verified":True,
"analytic_full_pep_verified":False,"lyapunov_proof_verified":False,"coefficient_formula_status":"candidate",
"evidence":["b4-static-002.json","b4-notebook-execution.json","b4-reconstruction-002-output.txt"],
"incidents":["Corrected generated-script string escape syntax before execution.","One exec launch rejected invalid cwd due to a transcription typo; no command ran or content was read.","Candidate kernel-value coefficient sign failed its numerical comparison; corrected to -1/(alpha*N) and reran all checks.","Split three semicolon-separated statements after Ruff diagnostics; final static checks passed."],
"consulted_sources_additional":["approved/plugins/pepflow-workflows/skills/lyap-vectors/references/workflow.md","approved/pepflow/lyapunov_utils.py","own B3 sources, certificate, rank evidence and generated B4 code"],
"access_control":"instruction_only","prohibited_content_observed":False,"unresolved_work":"B5 exact step, base, boundary and normalization proof, final notebook verification."}
(root/"supplementary/b4-handoff.json").write_text(json.dumps(record,indent=2))
print("B4 evidence and operational handoff complete.")
