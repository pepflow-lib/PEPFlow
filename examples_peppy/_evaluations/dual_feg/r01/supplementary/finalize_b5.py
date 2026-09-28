import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "dual_feg_example_lyap.ipynb"
nb = json.loads(path.read_text())
static = json.loads((root / "supplementary/b5-static-003.json").read_text())
execution = json.loads((root / "supplementary/b5-final-execution-002.json").read_text())
assert static["status"] == "passed" and execution["returncode"] == 0
texts = []
headings = {}
math_output_cells = []
for i, cell in enumerate(nb["cells"]):
    source = "".join(cell["source"])
    if cell["cell_type"] == "markdown":
        assert "\\(" not in source and "\\[" not in source
        assert not any(ord(c) < 32 and c not in "\n\t" for c in source)
        headings[i] = source.splitlines()[0] if source else ""
    else:
        assert cell["execution_count"] is not None
        for out in cell.get("outputs", []):
            assert out["output_type"] != "error"
            if "text" in out:
                texts.append((i, "".join(out["text"])))
            if "text/latex" in out.get("data", {}):
                math_output_cells.append(i)
proof_checks = None
for i, text in texts:
    for line in text.splitlines():
        if line.startswith("All exact proof checks:"):
            proof_checks = ast.literal_eval(line.split(":", 1)[1].strip())
        if any(
            word in line
            for word in [
                "exact all-component identity:",
                "exact-formula vs numerical",
                "Coefficient solution family:",
                "Labeled numerical Gram",
            ]
        ):
            print(i, line)
assert proof_checks is not None and all(proof_checks.values())
assert all(
    proof_checks.get(k)
    for k in [
        "step",
        "base",
        "last_step",
        "small_horizon",
        "boundary",
        "signs",
        "domain",
        "normalization",
    ]
)
assert any("Labeled numerical Gram" in t for _, t in texts)
assert any("sparse basis:" in t for _, t in texts)
assert any(
    "image/png" in out.get("data", {})
    for c in nb["cells"]
    for out in c.get("outputs", [])
)
print("Headings:", headings)
print("Cells containing labeled mathematical outputs:", math_output_cells)

b4 = json.loads((root / "state/dual_feg_b4.json").read_text())
formula = "V_0=0; for 1<=k<=N-1, V_k=-(4L/N)<x_0-x_N,G>-2||z_k||^2-4<z_k,G>+(4L/(N-k))<z_k+G,x_k-x_N>, G=A(x_N); V_N=2||G||^2-(4L/N)<x_0-x_N,G>."
interior_coeffs = {
    "0,0": "0",
    "0,1": "0",
    "0,2": "0",
    "0,3": "-2*L/N",
    "1,1": "-2",
    "1,2": "2*L/(N-k)",
    "1,3": "-2",
    "2,2": "0",
    "2,3": "2*L/(N-k)",
    "3,3": "0",
}
structure = {
    "quadratic_convention": "sum_ij C_ij <v_i,v_j> with symmetric C, off-diagonal entries counted twice",
    "interior": {
        "index_domain": "1<=k<=N-1 (empty when N=1)",
        "basis_labels": ["x_0-x_N", "z_k", "x_k-x_N", "A(x_N)"],
        "coefficients": interior_coeffs,
    },
    "initial": {
        "index_domain": "k=0",
        "basis_labels": [],
        "coefficients": {},
        "expression": "0",
    },
    "terminal": {
        "index_domain": "k=N, N>=1",
        "basis_labels": ["x_0-x_N", "A(x_N)"],
        "coefficients": {"0,0": "0", "0,1": "-2*L/N", "1,1": "2"},
    },
    "function_terms": [],
    "constant_terms": [],
}
coeff_source = (
    (root / "supplementary/b5_coeff_formula.py")
    .read_text(encoding="utf-8-sig")
    .split("\nformula_errors=", 1)[0]
)
local_source = "def local_multipliers(k,N,L):\n    t=sp.sympify(N-k)\n    if k==N-1:\n        return sp.Integer(2),sp.Integer(0)\n    return 2/t**2,4*sp.sympify(L)/(t*(t-1))\n"
arguments = {
    "domain": "N>=1 integer; L>0; R>=0. Interior formula uses k<N; ordinary steps t=N-k>=2; final t=1 and N=1 are checked separately.",
    "step": "Exact PEPFlow all-component identity with multipliers 2/t^2 and 4L/[t(t-1)] multiplying nonpositive Lipschitz and monotonicity residuals.",
    "base": "At z_0=0 the interior expression evaluated at k=0 is exactly zero; the N>=2 first-step identity is independently checked.",
    "last_step": "Actual x_N=x_{N-1}-(z_{N-1}+A(x_{N-1}))/L gives V_N-V_{N-1}=2 Lip(x_{N-1},x_N); N=1 is directly checked.",
    "boundary": "metric-4L^2R^2/N^2 = V_N+(4L/N)Mon(x_N,x_star)-||2L(x_0-x_star)/N-G||^2+(4L^2/N^2)(||x_0-x_star||^2-R^2). All right-hand terms are nonpositive.",
    "signs": "All residual multipliers are positive on their stated domains. The Euclidean square is nonnegative and subtracted. The initial residual is nonpositive by assumption.",
    "normalization": "Exact boundary coordinates include the constant 4L^2R^2/N^2; no R-versus-R-squared substitution is used.",
    "derivation": "Exact coefficient equations give a=-d/(2L), b=d, c=-d/L, nu=d/(2Lt^2), mu=d/[t(t-1)]. Set e=-d from V_0=0 and choose d=4L; exact base/terminal checks validate the normalization.",
}
state = {
    **b4,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": True,
    "proof_checks": proof_checks,
    "proof_arguments": arguments,
    "lyapunov_formula": formula,
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": structure,
    "coeff_code": coeff_source,
    "local_multiplier_code": local_source,
    "coefficient_formula_status": "verified",
    "unresolved_coefficients": [],
    "remaining_unknowns": [],
    "theorem": "For every integer N>=1, ||A(x_N)||^2 <= 4*L^2*R^2/N^2.",
    "numerical_certificate_verified": True,
    "run_status": "complete",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "unresolved_work": [],
    "notebook": "dual_feg_example_lyap.ipynb",
    "static_evidence": "supplementary/b5-static-003.json",
    "execution_evidence": "supplementary/b5-final-execution-002.json",
    "presentation_policy": "evaluation-ancillary-v1",
    "rendered_inspection_performed": False,
    "completed_utc": datetime.now(timezone.utc).isoformat(),
}
(root / "state/dual_feg_b5.json").write_text(json.dumps(state, indent=2))
items = [
    "title, problem description, and the algorithm update equations in LaTeX",
    "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
    "imports",
    "function/operator definitions",
    "make_ctx_dual_feg and get_pep_setup",
    "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
    "dense and relaxed proof solves",
    "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
    "partial-sum Lyapunov construction and rank profile",
    "special-vector identification",
    "coefficient extraction and closed-form V_k",
    "symbolic step, base, and boundary identities",
]
indices = [
    "0",
    "1,2,3",
    "4,5",
    "6",
    "7",
    "8,9",
    "10-14",
    "10-14",
    "15-20",
    "21-29",
    "30-38",
    "39-50",
]
evidence = [
    "Assumptions, metric and three algorithm updates present.",
    "Separate proof heading, theorem with full V_k and self-contained detailed proof outline present.",
    "Approved source/runtime paths; fresh-kernel execution succeeded.",
    "Lipschitz-monotone operator and L,R defined.",
    "Visible exact recursion, tags, R^2 constraint and residual metric.",
    "Seven values/statuses and image/png comparison plot present.",
    "Dense and sparse coherent solves at N=6; N=8 confirmation certificate.",
    "All dual groups, labeled true numerical S, complete LDL factors, candidate formulas and residual matrices; numerical checks passed; global analytic status remains explicit.",
    "Visible full-coordinate certificate replay and partial-sum loop; rank4 at N=6 and N=8 with fixed exclusions; coverage verified.",
    "Actual filtered candidate scan and sparse search output; adopted interior/endpoint bases verified.",
    "All-index numerical coefficients and component reconstruction; exact solved coefficient family, labeled formula matrices and complete closed-form V_k.",
    "Separate exact step, initial, final-step, N=1 and performance-boundary contexts; Gram/function/constant residuals zero; signs, domains and normalization justified.",
]
lines = [
    f"Notebook: {path.name}",
    "Last reviewed block: B5",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    "Presentation policy: evaluation-ancillary-v1. Markdown delimiters/control characters checked. Rendering and image inspection omitted under the explicit evaluation override; no rendered verification claimed.",
    "Static checks: supplementary/b5-static-003.json. Clean-kernel nbconvert execution: supplementary/b5-final-execution-002.json.",
    "",
    "| Item | Status | Cells (zero-based) | Evidence |",
    "|---|---|---|---|",
]
for i, (item, cell_ids, ev) in enumerate(zip(items, indices, evidence), 1):
    lines.append(f"| {i}. {item} | verified | {cell_ids} | {ev} |")
(root / "supplementary/dual_feg_example_lyap_checklist.md").write_text("\n".join(lines))
record = {
    "current_block": "B5",
    "access_control": "instruction_only",
    "approved_direct_reads": [
        "plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md",
        "pepflow/expression_manager.py",
    ],
    "generated_scripts": [
        "b5_derive.py",
        "run_b5_derive.py",
        "b5_step.py",
        "b5_base.py",
        "b5_last.py",
        "b5_boundary.py",
        "run_b5_exact.py",
        "b5_coeff_formula.py",
        "update_b5_notebook.py",
        "b5_static_repair.py",
        "execute_final_notebook.py",
        "b5_display_repair.py",
        "finalize_b5.py",
    ],
    "incidents": [
        {
            "classification": "static_diagnostics",
            "evidence": "b5-static-001.json",
            "reason": "Two symbolic parameter dictionaries exceeded the framework numerical-only type annotation.",
            "repair": "Explicit dict[str, Any] annotations on symbolic mappings; no framework or mathematical change.",
        },
        {
            "classification": "notebook_content_gap",
            "reason": "Labeled true numerical S was not displayed during initial final audit.",
            "repair": "Added its display and repeated static/final execution checks.",
        },
    ],
    "prohibited_sources_used_or_observed": False,
    "audit_limit": "Instruction-only read restrictions; no exhaustive OS read trace. Actual tool outputs and adapter source manifests retained.",
    "run_status": "complete",
}
(root / "supplementary/b5-access-record.json").write_text(json.dumps(record, indent=2))
closure = {
    "current_block": "B5",
    "completion_status": "complete",
    "next_block": None,
    "entry_exit_reason": "All mathematical proof obligations, notebook content checks, static checks and final clean-kernel execution passed.",
    "run_status": "complete",
    "stop_status": "final_attempt_closure",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "unresolved_work": [],
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": True,
    "original_deadline_utc": "2026-09-23T17:28:27.146339+00:00",
    "completed_utc": state["completed_utc"],
    "notebook": str(path),
    "state": "state/dual_feg_b5.json",
    "access_control": "instruction_only",
    "prohibited_sources_used_or_observed": False,
    "access_audit_limit": record["audit_limit"],
    "consulted_source_records": [
        "supplementary/preflight-access-record.json",
        "supplementary/b1-access-record.json",
        "supplementary/b2-access-record.json",
        "supplementary/b2-n8-access-record.json",
        "supplementary/b3-access-record.json",
        "supplementary/b4-access-record.json",
        "supplementary/b5-access-record.json",
    ],
    "provider_usage": None,
}
(root / "supplementary/final-handoff.json").write_text(json.dumps(closure, indent=2))
print("B5 complete. Notebook SHA256:", hashlib.sha256(path.read_bytes()).hexdigest())
