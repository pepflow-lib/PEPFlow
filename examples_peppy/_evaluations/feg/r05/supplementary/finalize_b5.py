import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "feg_example_lyap.ipynb"
nb = json.loads(path.read_text())
stream = "\n".join(
    "".join(o.get("text", []))
    for c in nb["cells"]
    for o in c.get("outputs", [])
    if o["output_type"] == "stream"
)
for c in nb["cells"]:
    source = "".join(c["source"])
    assert "\x0c" not in source and "\r" not in source
    if c["cell_type"] == "markdown":
        assert "\\(" not in source and "\\[" not in source
        assert source.count("$$") % 2 == 0
    if c["cell_type"] == "code":
        assert c["execution_count"] is not None
        assert all(o["output_type"] != "error" for o in c.get("outputs", []))
proof_checks = {
    "step": "Step all scalar components exactly zero." in stream,
    "base": "Base U_1-U_0=Lip(x_0,x_1) all scalar components exactly zero." in stream,
    "boundary": "Boundary all scalar components exactly zero." in stream,
    "signs": "all residual multipliers are nonnegative and denominators are nonzero."
    in stream,
    "domain": "N=1 uses only base and boundary; R=0 is covered without dividing by R."
    in stream,
    "normalization": "hence N^2 ||A(x_N)||^2 <= 4 L^2 ||x_0-x_star||^2 <= 4 L^2 R^2."
    in stream,
}
assert all(proof_checks.values())
assert any("image/png" in o.get("data", {}) for o in nb["cells"][11]["outputs"])
for i in [17, 19, 35, 43, 47, 50, 53]:
    assert any(o["output_type"] == "display_data" for o in nb["cells"][i]["outputs"])
static = json.loads((root / "supplementary/b5-static-001.json").read_text())
assert all(
    c["returncode"] == 0
    for c in static["commands"]
    if c["label"] in ["source_ruff", "source_ty"]
)
assert (
    "Numerical certificate verified: True; analytic full-PEP formula verified: False; analytic Lyapunov proof verified: True"
    in stream
)
b4 = json.loads((root / "state/feg_b4.json").read_text())
case = dict(
    index_domain="1 <= k <= N-1",
    basis_labels=["A(x_k)", "x_k-x_0"],
    quadratic_coefficients={"00": "k**2", "01": "k*L", "11": "0"},
)
structure = dict(
    quadratic_convention="sum_ij C_ij <v_i,v_j>; symmetric C; offdiagonal counted twice",
    interior=case,
    initial=dict(index_domain="k=0", basis_labels=[], quadratic_coefficients={}),
    terminal=dict(
        index_domain="k=N",
        basis_labels=["A(x_N)", "x_N-x_0"],
        quadratic_coefficients={"00": "N**2", "01": "N*L", "11": "0"},
    ),
    function_terms=[],
    constant_terms=[],
)
state = dict(
    b4,
    lyapunov_proof_verified=True,
    analytic_full_pep_verified=False,
    proof_checks=proof_checks,
    proof_arguments=dict(
        step="Exact symbolic Gram/function/offset identity, notebook cell 47; multipliers (k+1)^2 and 2k(k+1)L are positive for k>=1,L>0.",
        base="Separate shared-point first-step context, cell 50: V1=Lip(x0,x1)<=0 and V0=0.",
        boundary="Cell 53 verifies N^2||gN||^2-4L^2||d||^2=2VN+4NL Mon(xN,xstar)-||NgN-2Ld||^2. Every RHS term is nonpositive.",
        domain="Integers N>=1,k>=1; L>0,R>=0. N=1 has empty interior recursion. No division by R.",
        normalization="Use initial ||d||^2<=R^2 and divide by N^2>0; positive potential scaling chosen a1=1.",
    ),
    lyapunov_formula="V_0=0; V_k=k^2*||A(x_k)||^2+2*k*L*<A(x_k),x_k-x_0> for 1<=k<=N",
    discovery_expression_structure=b4["expression_structure"],
    expression_structure=structure,
    coeff_code="def coeff_pattern(k, L):\n    return sp.zeros(0, 0) if k == 0 else sp.Matrix([[k**2, k*L], [k*L, 0]])",
    local_multiplier_code="def step_multipliers(k, L):\n    return (k+1)**2, 2*k*(k+1)*L\n# Base Lipschitz multiplier: 1. Terminal monotonicity multiplier: 4*N*L; square coefficient: 1.",
    coefficient_formula_status="verified",
    unresolved_coefficients=[],
    remaining_unknowns=[],
    numerical_normalization_note="The saved numerical partial sums have positive solver-dependent scale sigma=coeff_by_k[1][0][0]. The exact potential fixes a1=1; coefficient comparisons after rescaling pass without modifying the numerical certificate.",
    theorem="For integer N>=1, ||A(x_N)||^2 <= 4*L**2*R**2/N**2.",
    run_status="completed",
    completion_status="complete",
    completed_blocks=["B1", "B2", "B3", "B4", "B5"],
    unresolved_work=[
        "Global full-PEP closed forms remain unverified; not required for the completed analytic Lyapunov theorem."
    ],
    final_validation=dict(
        static_evidence="supplementary/b5-static-001.json",
        clean_kernel_execution="supplementary/final-nbconvert-console.txt",
        presentation_policy="evaluation-ancillary-v1",
        rendered_review="not performed under evaluation override",
        notebook_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    ),
)
(root / "state/feg_b5.json").write_text(json.dumps(state, indent=2, allow_nan=False))
labels = [
    "title, problem description, and the algorithm update equations in LaTeX",
    "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
    "imports",
    "function/operator definitions",
    "make_ctx_feg and get_pep_setup",
    "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
    "dense and relaxed proof solves",
    "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
    "partial-sum Lyapunov construction and rank profile",
    "special-vector identification",
    "coefficient extraction and closed-form V_k",
    "symbolic step, base, and boundary identities",
]
evidence = [
    "0: full assumptions, both updates, shared initial half point, metric",
    "1-3: separate theorem and self-contained detailed proof; explicit potential and exact constant",
    "4,5: approved roots and executable imports",
    "7: L-Lipschitz monotone operator, L and R",
    "9: actual context builder, initial R squared constraint, terminal squared residual",
    "10-12: seven optimal values and saved PNG comparison plot output",
    "13,14,20,21: dense and sparse solve records at N=6,8; support and bound-preservation checks",
    "15-19: complete numerical identity and LDL reconstruction, true S and candidate displays, candidate failures and unresolved global status",
    "22-24: visible source/coordinate replay, actual grouping loop, rank printout, fixed-exclusion N=6,8 comparison and coverage",
    "25-33: rich candidate scan, actual sparse-basis search output at each index, adopted interpretable template and independence",
    "34-44: all-index full-coordinate numerical reconstruction, unknown-coefficient elimination, exact recurrence and positive normalization, labeled exact C and comparison",
    "45-55: separate symbolic PEPFlow step/base/boundary identities with labeled zero residuals in all scalar components, complete sign/domain and normalization argument",
]
lines = [
    "Notebook: feg_example_lyap.ipynb",
    "Last reviewed block: B5",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    "Presentation policy: evaluation-ancillary-v1. Executed source/output audit; no rendered/image review performed or claimed.",
    "",
    "| Item | Status | Cells and evidence |",
    "|---|---|---|",
]
lines += [
    f"| {i}. {label} | verified | {ev} |"
    for i, (label, ev) in enumerate(zip(labels, evidence), 1)
]
(root / "supplementary/feg_example_lyap_checklist.md").write_text("\n".join(lines))
p = root / "supplementary/preflight-access-record.json"
r = json.loads(p.read_text(encoding="utf-8-sig"))
r["B5_reads"] = [
    "approved lyap-closed-form/references/workflow.md",
    "approved pepflow/expression_manager.py",
    "Own B4 state and generated final symbolic sources/notebook/output evidence",
]
r["B5_commands"] = [
    "run_b5.py exact coefficient elimination and symbolic identities",
    "notebook_b5.py source update",
    "adapter b5-static-001.json",
    "execute_final.py: pinned python -I -B -m nbconvert --execute with private kernel",
    "finalize_b5.py source/output audit and state save",
]
r["incidents"] += [
    {
        "kind": "source_diagnostics",
        "evidence": "b3-static-001.json",
        "repair": "Added explicit integer type guard and reran grouping, notebook and b3-static-002.json",
    },
    {
        "kind": "source_diagnostics",
        "evidence": "b4-static-001.json",
        "repair": "Typed parameter dictionary and distinct replay import alias; b4-static-002 passed",
    },
    {
        "kind": "operational",
        "reason": "Final audit command used a mistyped nonexistent working directory; process creation failed before any command ran",
        "repair": "Repeated read-only audit in actual attempt directory; no content exposure",
    },
]
r["status"] = "completed B1-B5"
r["prohibited_sources_observed"] = False
r["access_control"] = "instruction_only"
r["visibility_limit"] = (
    "No exhaustive OS read tracing. Declaration covers observed tools and approved dependency/runtime imports; no claim of OS-enforced isolation or training-source independence."
)
r["integrity_exceptions"] = (
    "Operational/source-check repairs documented; no known prohibited mathematical source exposure."
)
p.write_text(json.dumps(r, indent=2))
(root / "supplementary/final-handoff.json").write_text(
    json.dumps(
        dict(
            current_block="B5",
            completion_status="complete",
            next_block=None,
            entry_exit_reason="Analytic theorem and all required notebook checks complete",
            run_status="completed",
            operational_status="stopped_after_completion",
            unresolved_work=state["unresolved_work"],
        ),
        indent=2,
    )
)
print("Final notebook audit passed. B5 state and closure evidence saved.")
print("Notebook SHA-256:", hashlib.sha256(path.read_bytes()).hexdigest())
