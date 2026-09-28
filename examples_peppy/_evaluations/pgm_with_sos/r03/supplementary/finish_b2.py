import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
path=root/"pgm_example_lyap.ipynb"
nb=json.loads(path.read_text())
summaries=[]
for i,c in enumerate(nb["cells"]):
    source="".join(c["source"])
    if c["cell_type"]=="markdown":
        assert not any(x in source for x in ("\\(","\\)","\\[","\\]","\r","\f"))
        assert source.count("$")%2==0
    else:
        assert c["execution_count"] is not None
        assert not any(o["output_type"]=="error" for o in c["outputs"])
    texts=["".join(o.get("text","")) for o in c.get("outputs",[]) if o["output_type"]=="stream"]
    summaries.append({"index":i,"id":c["id"],"type":c["cell_type"],
                      "first_line":source.splitlines()[0] if source else "",
                      "outputs":texts,"display_count":sum(o["output_type"]=="display_data" for o in c.get("outputs",[]))})
print(json.dumps(summaries,indent=2))
state=json.loads((root/"state/pgm_b2.json").read_text())
for p,h in state["certificate_provenance"]["source_hashes"].items():
    assert hashlib.sha256((root/p).read_bytes()).hexdigest()==h
ckpath=root/"supplementary/pgm_example_lyap_checklist.md"
text=ckpath.read_text()
text=text.replace("Last reviewed block: B1","Last reviewed block: B2")
lines=text.splitlines()
lines=[("SHA-256: "+hashlib.sha256(path.read_bytes()).hexdigest()) if l.startswith("SHA-256:") else l for l in lines]
for i,l in enumerate(lines):
    if l.startswith("| 7 |"):
        lines[i]="| 7 | dense and relaxed proof solves | verified | 10,11 | Dense and selected values, both owners, basis and S spectrum; fresh sparse solve provenance retained. |"
    if l.startswith("| 8 |"):
        lines[i]="| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 12,13,14,15,16,17 | Executed candidates and complete numerical coordinate checks; labeled candidate and residual matrices; exact fixed-N identity; global analytic flags false. |"
ckpath.write_text("\n".join(lines),encoding="utf-8")
record={"current_block":"B2","completion_status":"complete","next_block":"B3",
"entry_exit_reason":"Dense and sparse coherent certificates, initial formula search, numerical identity and decomposition gates, notebook execution and static checks completed",
"operational_status":"awaiting_same_session_continuation",
"numerical_certificate_verified":True,"analytic_full_pep_verified":False,"lyapunov_proof_verified":False,
"unresolved_work":"Arbitrary-horizon proof and B3-B5",
"certificate_id":state["certificate_id"],
"checks":state["numerical_checks"],"static_evidence":"supplementary/b2-static-003.json",
"execution_evidence":"supplementary/b2-notebook-console-003.txt",
"consulted_sources_additional":[
"approved/plugins/pepflow-workflows/skills/pep-full-proof/references/workflow.md",
"approved/pepflow/expression_manager.py","approved/pepflow/scalar.py",
"approved/pepflow/lyapunov_utils.py","approved/pepflow/parameter.py","approved/pepflow/__init__.py",
"Approved framework exact source hashes through certificates.fingerprint; own generated B1/B2 sources, states, notebook, and logs"],
"commands":["PowerShell exact-path reads/searches","Pinned Python -I -B: b2_dense.py, b2_sparse.py, finalize_b2.py, update_b2_notebook.py",
"Approved adapter b2-static-001 through 003; source diagnostics preserved",
"Pinned Python -I -B supplementary/finish_b2.py"],
"incidents":[
"Unused notebook import removed and source checks rerun",
"Source hash capture was initially after solve; capture routine corrected to pre/post solve checks and new coherent dense/sparse samples obtained. Initial sample preserved under supplementary/b2-initial-sample",
"Nonfatal Jupyter comm/cleanup warnings; notebook cells completed without execution errors"],
"access_control":"instruction_only","prohibited_content_observed":False,
"audit_limit":"No exhaustive OS-level tracing; adapter evidence and declared source records preserved"}
(root/"supplementary/b2-handoff.json").write_text(json.dumps(record,indent=2))

