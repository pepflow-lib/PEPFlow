"""Audit the executed notebook and record the completed B5 result."""

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "ogm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
b4 = json.loads((ROOT / "state" / "ogm_b4.json").read_text())
static = json.loads((ROOT / "supplementary" / "b5-static-002.json").read_text())
assert all(
    command["returncode"] == 0
    for command in static["commands"]
    if command["label"] in ("source_ruff", "source_ty")
)
codes = [cell for cell in nb.cells if cell.cell_type == "code"]
assert [cell.execution_count for cell in codes] == list(range(1, len(codes) + 1))
assert not any(
    output.output_type == "error" for cell in codes for output in cell.outputs
)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert not any(s in cell.source for s in ("\x0c", "\r", "\\(", "\\["))
        assert "pending Block" not in cell.source
streams = "\n".join(
    output.text
    for cell in codes
    for output in cell.outputs
    if output.output_type == "stream"
)
for expected in (
    "Generic step function residual: Matrix([[0, 0, 0]]) offset: 0",
    "Base step function residual: Matrix([[0, 0, 0]]) offset: 0",
    "Terminal identity function residual: Matrix([[0, 0]]) offset: 0",
    "Radius normalization function residual: Matrix([[0, 0]]) offset: 0",
    "N=1 terminal identity function residual: Matrix([[0, 0, 0]]) offset: 0",
    "All exact identities passed.",
):
    assert expected in streams, expected
assert any(
    "image/png" in output.get("data", {}) for cell in codes for output in cell.outputs
)
symbolic_source = (ROOT / "supplementary" / "b5_symbolic_cells.py").read_text()
for chunk in symbolic_source.split("# %% ")[1:]:
    body = chunk.split("\n", 1)[1]
    assert any(cell.source.strip() == body.strip() for cell in codes)
formula_source = (ROOT / "supplementary" / "b5_formula_cells.py").read_text()
assert any(cell.source == formula_source for cell in codes)
comparisons_text = next(
    line
    for line in streams.splitlines()
    if line.startswith("Full potential comparisons at N=4,6: ")
)
comparisons = ast.literal_eval(comparisons_text.split(": ", 1)[1])
assert (
    len(comparisons) == 12
    and max(
        max(row[key] for key in ("gram", "function", "offset")) for row in comparisons
    )
    < 1e-5
)
now = datetime.now(timezone.utc)
deadline = datetime.fromisoformat("2026-09-23T20:02:47.999904+00:00")
assert now < deadline
notebook_hash = hashlib.sha256(path.read_bytes()).hexdigest()
final_formula = "V_k = L/(2*T^2)*(||z_k-x_star||^2-||x_0-x_star||^2) + 2*theta_{k-1}^2/T^2*(f(x_k)-f_star) + theta_{k-1}^2/(L*T^2)*||g_k||^2 + 2*rho_k/T^2*<g_k,x_k-z_k>; T=theta_N, rho_k=theta_k for k<N and T/2 for k=N, theta_{-1}=0."
structure = {
    "quadratic_convention": "sum_i,j C_ij <v_i,v_j>, symmetric C; off-diagonal entries occur twice",
    "interior": {
        "index_domain": "2<=k<=N; left=2 right=0 discovery exclusions",
        "basis_labels": ["x_0-x_star", "z_k-x_star", "x_k-x_star", "g_k"],
        "coefficients": {
            "C00": "-L/(2*T^2)",
            "C11": "L/(2*T^2)",
            "C13=C31": "-rho_k/T^2",
            "C23=C32": "rho_k/T^2",
            "C33": "theta_{k-1}^2/(L*T^2)",
            "all_other_entries": "0",
        },
        "rho_k": "theta_k if k<N; T/2 if k=N",
    },
    "initial": {
        "index_domain": "k=0,1",
        "cases": {
            "0": {"basis_labels": [], "potential": "0"},
            "1": {
                "basis_labels": ["x_0-x_star", "z_1-x_star", "g_1"],
                "coefficients": {
                    "C00": "-L/(2*T^2)",
                    "C11": "L/(2*T^2)",
                    "C02=C20": "1/(2*theta_1*T^2)",
                    "C12=C21": "-1/(2*theta_1*T^2)",
                    "C22": "1/(L*T^2)",
                    "all_other_entries": "0",
                },
                "small_horizon": "For N=1, theta_1=T=2; exact first and terminal identities checked.",
            },
        },
    },
    "terminal": {
        "index_domain": "No separate excluded terminal index; k=N uses rho_N=T/2 in its applicable interior or N=1 initial formula."
    },
    "function_terms": [
        {
            "index_domain": "0<=k<=N",
            "expression": "f(x_k)-f_star",
            "coefficient": "2*theta_{k-1}^2/T^2",
        }
    ],
    "constant_terms": [],
}
proof_arguments = {
    "derivation": "Exact PEPFlow Gram/function/offset equations solve the sparse ansatz jointly with local multipliers, after fixing the radius coefficient a=1/2. Derived (a,b,c,d,m,n)=(1/2,2,1,2,2,2).",
    "step": "For k<N, theta_{k-1}^2=theta_k^2-theta_k. For both next-index recurrences, rho_{k+1}(theta_{k+1}-1)=theta_k^2. Substitution into the exact generic identity yields V_{k+1}-V_k = 2*theta_k/T^2 I_star,k + 2*theta_k^2/T^2 I_k,k+1.",
    "base": "z_0=x_0 and theta_{-1}=0 imply V_0=0. A separate symbolic initial-update context verifies the first increment and three-vector initial coefficient reduction.",
    "boundary": "gap_N - L/(2*T^2)||x_0-x_star||^2 = V_N + I_star,N/T - L/(2*T^2)||z_N-x_star-T*g_N/L||^2, checked exactly in all coordinates.",
    "signs": "Smooth convex interpolation gives I<=0. L>0, theta_k>=1, and T>=2 make every step, terminal, normalization, and square coefficient positive. Consequently V decreases; terminal residual and negative square have the required upper-bound sign.",
    "domain": "Every integer N>=1, real finite-dimensional Euclidean space, L>0, R>=0. Recurrence induction gives theta_k>=1 and every next theta>1, so all denominators are nonzero. N=1 (T=2) checked separately. No division by R is used.",
    "normalization": "The exact radius identity includes L/(2*T^2)*(||x_0-x_star||^2-R^2). Combining its nonpositivity with V_N<=0 and the boundary signs proves gap_N<=L*R^2/(2*T^2).",
    "global_certificate": "Sum the exact local identities from k=0 through N-1, use V_0=0, and substitute the boundary identity. This proves the full global lambda and rank-one S formulas, including the initial constraint offset. See the final notebook telescoping equation.",
}
state = {
    **b4,
    "coefficient_formula_status": "verified",
    "formula_status": {"lambda": "verified", "S": "verified"},
    "analytic_full_pep_verified": True,
    "lyapunov_proof_verified": True,
    "proof_checks": {
        name: True
        for name in ("step", "base", "boundary", "signs", "domain", "normalization")
    },
    "proof_arguments": proof_arguments,
    "lyapunov_formula": final_formula,
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": structure,
    "coeff_code": formula_source.split("def closed_form_potential", 1)[0],
    "analytic_potential_code": "def closed_form_potential"
    + formula_source.split("def closed_form_potential", 1)[1].split(
        "formula_comparisons =", 1
    )[0],
    "local_multiplier_code": "step_RHS = 2*t_exact/T_exact**2*I_star_step+2*t_exact**2/T_exact**2*I_forward_step\nboundary_RHS = V_terminal+I_terminal/T_exact-terminal_square",
    "unresolved_coefficients": [],
    "remaining_unknowns": [],
    "theorem": "f(x_N)-f(x_star) <= L*R^2/(2*theta_N^2)",
    "run_status": "completed",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "unresolved_work": [],
    "notebook_path": path.name,
    "notebook_sha256": notebook_hash,
    "static_evidence": "supplementary/b5-static-002.json",
    "execution_evidence": "supplementary/b5-final-nbconvert-output-002.txt",
    "symbolic_source": "supplementary/b5_symbolic_cells.py",
    "formula_comparisons": comparisons,
    "finished_utc": now.isoformat(),
    "original_deadline_utc": deadline.isoformat(),
    "presentation_policy": "evaluation-ancillary-v1",
    "rendered_review_performed": False,
}
(ROOT / "state" / "ogm_b5.json").write_text(
    json.dumps(state, indent=2, allow_nan=False)
)
items = [
    "title, problem description, and the algorithm update equations in LaTeX",
    "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
    "imports",
    "function/operator definitions",
    "make_ctx_ogm and get_pep_setup",
    "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
    "dense and relaxed proof solves",
    "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
    "partial-sum Lyapunov construction and rank profile",
    "special-vector identification",
    "coefficient extraction and closed-form V_k",
    "symbolic step, base, and boundary identities",
]
references = [
    "0",
    "1,2,3",
    "4,11,24,38",
    "6",
    "6",
    "7,8,9",
    "10,11,12,17,18",
    "13,14,15,16,57",
    "19,20,21,22",
    "23,24,25,26,27,28,29,30",
    "31,32,33,34,39,47,55,56",
    "40,41,42,43,44,45,48,49,50,51,52,53,54,57",
]
evidence = [
    "Algorithm, smooth-convex assumptions, special terminal theta, radius squared and metric present.",
    "Separate heading, theorem and proof outline contain explicit potential and detailed decrease/boundary identities.",
    "Approved source roots and required imports present and executed.",
    "SmoothConvexFunction and L,R definitions visible.",
    "Context builder and setup interface visibly encode the actual recursion and normalization.",
    "Seven optimal numerical values, candidate curve and actual PNG plot output present.",
    "Dense and sparse solve source, saved coherent results, support and preserved optimum displayed; N6 certificate separately retained.",
    "Numerical multipliers, true labeled S, spectral reconstruction, candidate lambda/S displays, full-coordinate residuals and exact global proof present.",
    "Actual partial-sum loop, all-coordinate coverage and rank output at N4,N6; fixed exclusions (2,0).",
    "Deduplicated candidate scan, actual sparse search, adopted local basis and endpoint independence executed.",
    "All-index numerical matrix and scalar reconstruction; exact coefficient derivation and labeled formula comparisons present.",
    "Separate symbolic contexts construct LHS,RHS,diff; all Gram/function/offset residuals zero. Normalization, N1, sign/domain and telescoping arguments present.",
]
lines = [
    f"Notebook: {path.name}",
    "Last reviewed block: B5",
    f"SHA-256: {notebook_hash}",
    "Presentation policy: evaluation-ancillary-v1. Source delimiters and controls checked. No browser, rendering or image inspection performed; the frozen override applies.",
    "Static: supplementary/b5-static-002.json; clean kernel: supplementary/b5-final-nbconvert-output-002.txt.",
    "",
    "| Item | Requirement | Status | Cells (zero-based) | Evidence |",
    "|---|---|---|---|---|",
]
for index, (item, cells, entry) in enumerate(zip(items, references, evidence), 1):
    lines.append(f"| {index} | {item} | verified | {cells} | {entry} |")
(ROOT / "supplementary" / "ogm_example_lyap_checklist.md").write_text("\n".join(lines))
audit = dict(
    run_status="completed",
    current_block="B5",
    completion_status="complete",
    next_block=None,
    entry_exit_reason="Exact step/base/boundary and sign/domain/normalization obligations established; final static, clean-kernel and content checks passed",
    operational_status="stopped_completed",
    completed_blocks=state["completed_blocks"],
    unresolved_work=[],
    notebook_sha256=notebook_hash,
    code_cells_executed=len(codes),
    access_control="instruction_only",
    prohibited_sources_observed=False,
    access_status="no_observed_prohibited_exposure",
    limitations="Instruction-only isolation and available tool logs; no exhaustive OS read tracing or claim about model training knowledge. No rendering performed under the frozen presentation policy.",
    consulted_source_records=[
        "preflight-access-record.json",
        "b1-handoff-access.json",
        "b2-handoff-access.json",
        "b3-return-b2.json",
        "b2-N6-handoff.json",
        "b3-handoff-access.json",
        "b4-handoff-access.json",
    ],
    additional_consulted_sources=[
        "Approved lyap-closed-form workflow",
        "Approved function.py interpolation implementation",
        "Approved parameter.py evaluation implementation",
        "Approved expression_manager.py symbolic evaluation implementation",
        "Own symbolic, notebook, state and static evidence files",
    ],
    commands="Pinned Python -I -B run_b5_symbolic.py; own notebook preparation/refinement; reviewed static adapter check; pinned Python -I -B -m nbconvert --execute twice; own output inspection and closure audit",
    incidents=[
        "Initial N=1 check used the prior global context; selected the owned base context explicitly and reran every symbolic check successfully. No frozen source changed.",
        "Earlier operational/static repairs remain recorded in existing handoffs; no mathematical criterion relaxed.",
    ],
    finished_utc=now.isoformat(),
    original_deadline_utc=deadline.isoformat(),
    token_usage=None,
)
(ROOT / "supplementary" / "final-audit.json").write_text(json.dumps(audit, indent=2))
print(
    json.dumps(
        {
            "run_status": "completed",
            "notebook_sha256": notebook_hash,
            "code_cells_executed": len(codes),
            "proof_checks": state["proof_checks"],
            "unresolved_work": [],
        }
    )
)
