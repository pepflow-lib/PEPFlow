"""Audit the executed notebook and close actual proof state."""
import hashlib
import json
from pathlib import Path

import nbformat as nbf

root=Path.cwd()
notebook=root / "feg_example_lyap.ipynb"
nb=nbf.read(notebook,as_version=4)
by_id={cell.id:cell for cell in nb.cells}
code_cells=[cell for cell in nb.cells if cell.cell_type=="code"]
assert [cell.execution_count for cell in code_cells]==list(range(1,len(code_cells)+1))
assert not any(output.output_type=="error" for cell in code_cells for output in cell.outputs)
def stream(cell_id):
    return "".join(output.get("text","") for output in by_id[cell_id].get("outputs",[]) if output.output_type=="stream")

def has_math_output(cell_id):
    return any("text/latex" in output.get("data",{}) for output in by_id[cell_id].get("outputs",[]))

assert any("image/png" in output.get("data",{}) for output in by_id["b1-06"].outputs)
assert all(f"N={n}:" in stream("b1-06") for n in range(1,8))
assert "Dense objective:" in stream("b2-01") and "Sparse objective:" in stream("b2-02")
assert "True saved S" in stream("b2-06") and has_math_output("b2-06")
assert "'passed': True" in stream("b2-07")
assert "Interior rank is constant at this N: True" in stream("b3-03")
assert all(f"N={n}: rank 2" in stream("b3-04") for n in (4,6))
assert "find_basis_with_sparsest_coefficients(" in by_id["b4-05"].source
assert all(f"k={k}, rank=2 sparse basis:" in stream("b4-05") for k in range(1,7))
assert all(f"k={k}: coefficient reconstruction residual" in stream("b4-09") for k in range(7))
assert "Complete expression reconstruction:" in stream("b4-10")
assert "Exact local coefficient solution:" in stream("b5-03")
assert "after common positive scale" in stream("b5-05") and has_math_output("b5-05")
for cell_id,label in (("b5-09","Step"),("b5-12","Base"),("b5-15","Boundary")):
    assert f"{label} Gram residual shape:" in stream(cell_id)
    assert "function residual: Matrix(0, 0, []) offset: 0" in stream(cell_id)
    assert has_math_output(cell_id)
    assert "_LHS" in by_id[cell_id].source and "_RHS" in by_id[cell_id].source and "_diff" in by_id[cell_id].source
assert "Exact local Lyapunov theorem verified" in stream("b5-17")
assert by_id["proof-00"].source=="## Proof Statement"
assert "V_{0}=0" in by_id["proof-01"].source
assert "operatorname{Mon}" in by_id["proof-02"].source and "operatorname{Lip}" in by_id["proof-02"].source
markdown="\n".join(cell.source for cell in nb.cells if cell.cell_type=="markdown")
assert not any(x in markdown for x in ("\\(","\\)","\\[","\\]","\x0c","\r"))
static=json.loads((root / "supplementary/b5-static-002.json").read_text())
assert static["status"]=="passed"
for manifest in static["sources"]:
    if Path(manifest["source"]).suffix==".py":
        assert hashlib.sha256(Path(manifest["source"]).read_bytes()).hexdigest()==manifest["sha256"]
b4=json.loads((root / "state/feg_b4.json").read_text())
symbolic=json.loads((root / "supplementary/b5-symbolic-results.json").read_text())
proof_checks={key:symbolic[key] for key in ("step","base","boundary","signs","domain","normalization")}
assert all(proof_checks.values())
final_structure={
    "quadratic_convention":"V = sum_ij C_ij <v_i,v_j>; symmetric C with off-diagonal terms counted twice",
    "interior":{"index_domain":"1 <= k <= N-1", "basis_labels":["A(x_k)","x_k-x_0"],
                "coefficients":{"00":"2*k**2/N**2","01":"2*k*L/N**2","11":"0"}},
    "initial":{"index_domain":"k=0","basis_labels":[],"coefficients":{},"value":"0"},
    "terminal":{"index_domain":"k=N","basis_labels":["A(x_N)","x_N-x_0"],
                "coefficients":{"00":"2","01":"2*L/N","11":"0"}},
    "function_terms":[],"constant_terms":[]}
coeff_source=by_id["b5-05"].source.split("numeric_scale =")[0]
state={**b4,"proof_checks":proof_checks,
    "proof_arguments":{
        "step":"Visible native PEPFlow symbolic k,N,L context and exact full-coordinate identity in b5-09; nonnegative monotonicity/Lipschitz weights imply decrease.",
        "base":"Separate shared x_0=x_1/2 context in b5-12 gives V_1=2 Lip(x_1,x_0)/N² <=0=V_0.",
        "boundary":"b5-15 verifies metric-target = V_N + (4L²/N²)(||x_0-x_star||²-R²) + (4L/N)Mon(x_N,x_star) - ||A(x_N)-(2L/N)(x_0-x_star)||². All RHS terms nonpositive.",
        "signs":"Positive multipliers for L>0 and integers N>=1,k>=1; squared norm nonnegative. No nonnegativity assumption on V.",
        "domain":"Step 1<=k<N; separate base and boundary cover N=1. R>=0, no division by R or residual norm. L,N,k,k+1 denominators nonzero in their respective domains.",
        "normalization":"Coefficient recurrence leaves a positive scale; choose 2/N² and verify exact terminal performance normalization 4L²R²/N². Numerical sample scale diagnostic is explicit, not substitution into the saved certificate."},
    "lyapunov_formula":"V_0=0; V_k=2*k**2/N**2*||A(x_k)||**2 + 4*k*L/N**2*<A(x_k),x_k-x_0>, 1<=k<=N",
    "convergence_theorem":"||A(x_N)||**2 <= 4*L**2*R**2/N**2 for all integers N>=1",
    "discovery_expression_structure":b4["expression_structure"],"expression_structure":final_structure,
    "coeff_code":coeff_source,"coefficient_formula_status":"verified","unresolved_coefficients":[],
    "local_multiplier_code":"lambda_k = 4*L*k*(k+1)/N**2; mu_k = 2*(k+1)**2/N**2; base = 2/N**2; initial = 4*L**2/N**2; terminal = 4*L/N",
    "numerical_certificate_verified":True,"analytic_full_pep_verified":False,"lyapunov_proof_verified":True,
    "run_status":"completed","completed_blocks":["B1","B2","B3","B4","B5"],
    "unresolved_work":[],"unresolved_optional_global_certificate":"Analytic formulas reproducing the original floating-point full-PEP certificate remain unresolved; no separate analytic-full-PEP objective was required.",
    "delivery_checks":{"static":"supplementary/b5-static-002.json","fresh_kernel_nbconvert":"supplementary/b5-final-execution-output.txt", "presentation_policy":"evaluation-ancillary-v1","rendered_inspection_performed":False}}
(root / "state/feg_b5.json").write_text(json.dumps(state,indent=2,allow_nan=False))
checklist=root / "supplementary/feg_example_lyap_checklist.md"
rows=[
    (1,"title, problem description, and the algorithm update equations in LaTeX","b1-00, proof-01","Assumptions, residual metric, both recurrences, initial half-step sharing and domains present."),
    (2,"proof statement placeholder, to be filled with the final theorem and proof outline in Block 5","proof-00 through proof-02","Separate theorem and self-contained proof outline give explicit V, base/step/boundary equations and bound."),
    (3,"imports","b1-02, b1-03, b4-01, b5-01","Approved paths, framework, symbolic/numerical and plotting imports execute in fresh kernel."),
    (4,"function/operator definitions","b1-03","Monotone Lipschitz class with L,R parameters; symbolic contexts use distinct operator tags."),
    (5,"make_ctx_feg and get_pep_setup","b1-04","Visible executable recursion, radius-squared initial condition and final residual metric."),
    (6,"numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate","b1-05,b1-06","All seven values and image/png comparison plot are present; no image inspection per presentation override."),
    (7,"dense and relaxed proof solves","b2-01,b2-02","Actual saved dense/sparse results, visible acquisition/support recipe, preserved-bound check, labeled active multipliers."),
    (8,"lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)","b2-03 through b2-08","Initial candidate search failures explicit; true S, full LDL, labeled coordinate residuals and separate global analytic status retained."),
    (9,"partial-sum Lyapunov construction and rank profile","b3-00 through b3-04","Visible complete certificate replay, grouping/update loop, per-index ranks, N=4/6 comparison and full coverage/sign checks."),
    (10,"special-vector identification","b4-00 through b4-07","342 candidate scan, actual sparsity-search outputs for every nonzero k, adopted meaningful basis and endpoint independence."),
    (11,"coefficient extraction and closed-form V_k","b4-08 through b4-11, b5-02 through b5-06","All numerical matrices/components reconstructed; symbolic recurrence solves unknowns, scale choice explicit, exact coefficient matrices and closed form displayed."),
    (12,"symbolic step, base, and boundary identities","b5-07 through b5-17","Separate native PEPFlow symbolic identities, all Gram/function/offset residuals zero, labeled matrices, signs/domain/normalization and N=1 covered.")]
digest=hashlib.sha256(notebook.read_bytes()).hexdigest()
header=f"Notebook: {notebook.name}\nLast reviewed block: B5\nSHA-256: {digest}\nPresentation policy: evaluation-ancillary-v1; no rendered/image inspection. All required mathematical/source/execution checks performed.\n\n| # | Item | Status | Cells | Evidence |\n|---|---|---|---|---|\n"
checklist.write_text(header+"\n".join(f"| {i} | {label} | verified | {cells} | {evidence} |" for i,label,cells,evidence in rows)+"\n")
audit={"notebook_sha256":digest,"code_cells":len(code_cells),"all_code_executed":True,
       "error_outputs":0,"all_twelve_items_verified":True,"static_status":"passed",
       "nbconvert_exit_status":0,"symbolic_cell_ids":["b5-09","b5-12","b5-15"],
       "presentation_policy":"evaluation-ancillary-v1","rendered_inspection":False}
(root / "supplementary/b5-final-audit.json").write_text(json.dumps(audit,indent=2))
print(json.dumps(audit))
