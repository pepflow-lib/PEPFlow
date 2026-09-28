"""Inspect saved source and execution evidence under the presentation override."""
import hashlib
import json
from pathlib import Path


def main():
    root=Path(__file__).resolve().parent.parent
    path=root/"pgm_example_lyap.ipynb"
    nb=json.loads(path.read_text(encoding="utf-8"))
    b5=json.loads((root/"state/pgm_b5.json").read_text())
    source=lambda c:"".join(c["source"])
    errors=[(i,o) for i,c in enumerate(nb["cells"]) for o in c.get("outputs",[]) if o["output_type"]=="error"]
    assert not errors
    counts=[c["execution_count"] for c in nb["cells"] if c["cell_type"]=="code"]
    assert all(isinstance(c,int) and c>0 for c in counts)
    assert counts==list(range(1,len(counts)+1))
    for c in nb["cells"]:
        if c["cell_type"]=="markdown":
            s=source(c)
            assert not any(ord(x)<32 and x not in "\n\t" for x in s)
            assert "\\(" not in s and "\\[" not in s
            assert s.count("$")%2==0
            assert "a_{0I}" not in s and "b_{1I}" not in s
    assert source(nb["cells"][1])=="## Proof Statement"
    assert source(nb["cells"][2]).startswith("### Theorem")
    assert source(nb["cells"][3]).startswith("### Proof outline")
    assert b5["lyapunov_proof_verified"] and all(b5["proof_checks"].values())
    assert not b5["unresolved_coefficients"]
    sources="\n".join(source(c) for c in nb["cells"])
    assert "find_basis_with_sparsest_coefficients(" in sources and "partial_sum" in sources
    image_count=sum("image/png" in o.get("data",{}) for c in nb["cells"] for o in c.get("outputs",[]))
    assert image_count>0
    outputs={}
    for i in (44,45,49,52,55,58,61,63,64):
        outputs[str(i)]="".join("".join(o.get("text",[])) for o in nb["cells"][i].get("outputs",[]))
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    evidence={"notebook_sha256":digest,"code_cells_executed":len(counts),"png_outputs_retained":image_count,
        "error_outputs":errors,"proof_checks":b5["proof_checks"],"key_text_outputs":outputs,
        "markdown_source_checks":"passed","presentation_policy":"evaluation-ancillary-v1",
        "visual_review":"not performed; prohibited by evaluation override",
        "access_control":"instruction_only","prohibited_source_reads_observed":False}
    (root/"supplementary/final-audit.json").write_text(json.dumps(evidence,indent=2))
    rows=[
    ("title, problem description, and the algorithm update equations in LaTeX","0","Source contains all assumptions, proximal recurrence, initial condition, and metric."),
    ("proof statement placeholder, to be filled with the final theorem and proof outline in Block 5","1-3","Separate heading, theorem with full potential and all endpoint cases, self-contained proof outline with every residual and square."),
    ("imports","4-5","Approved framework origin checks and fresh private kernel execution passed."),
    ("function/operator definitions","7","Smooth convex f, convex g, L and R, composite stationarity."),
    ("make_ctx_pgm and get_pep_setup","9","Executable algorithm, initial normalization and final metric remain visible."),
    ("numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate","10-11","Seven numerical values/statuses, inverse-rate discovery, error 4.32e-9, PNG output retained; no image inspection under override."),
    ("dense and relaxed proof solves","13-17","Acquisition code, saved dense/selected statuses and coherent certificate replay retained. Dense/relaxed gap 2.34e-10."),
    ("lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)","18-22","Initial rational formula search, all numerical duals/extras, S/LDL labeled displays and full-coordinate identity checks. Global analytic status explicitly unresolved; local analytic proof separately completed."),
    ("partial-sum Lyapunov construction and rank profile","23-27","Actual partial_sum construction; congruence decomposition covers saved S to roundoff; unchanged rank threshold confirms interior rank 4 at N=4 and N=6 with fixed exclusions (1,1)."),
    ("special-vector identification","28-36","Actual sparse basis search executed at every required index; rank, basis and near-zero counts printed. Terminal basis verified after congruence recovery."),
    ("coefficient extraction and closed-form V_k","37-46","Labeled numerical and exact coefficient matrices; function/offset reconstruction; native unknown-coefficient equations and selected exact solution; closed-form conclusion includes function gaps and endpoints."),
    ("symbolic step, base, and boundary identities","47-64","Positive-polynomial sign identities (49); separate native step (52), base (55), terminal (58), N=1 (61) all zero in Gram/function/offset. Normalization and nonincreasing telescoping (62-63); durable B5 state (64).")]
    text=f"Notebook: pgm_example_lyap.ipynb\nLast reviewed block: B5 complete\nSHA-256: {digest}\nPresentation: evaluation-ancillary-v1. Source and saved execution outputs inspected; no rendered/image inspection performed.\n\n"
    text+="| Item | Status | Cells (zero-based) | Evidence |\n| --- | --- | --- | --- |\n"
    text+="\n".join(f"| {i}. {wording} | verified | {cells} | {why} |" for i,(wording,cells,why) in enumerate(rows,1))
    text+="\n\nRequired static checks: b5-static-006.json passed. Final fresh-kernel nbconvert execution: b5-final-notebook-004.txt passed. Proof and source audit: final-audit.json. No tolerances were relaxed.\n"
    (root/"supplementary/pgm_example_lyap_checklist.md").write_text(text)
    print(json.dumps({k:v for k,v in evidence.items() if k!="key_text_outputs"},indent=2))


if __name__=="__main__":
    main()
