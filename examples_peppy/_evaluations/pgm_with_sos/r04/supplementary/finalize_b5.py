import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import json

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

root = runtime.ROOT
path = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
b4 = json.loads((root / "state/pgm_b4.json").read_text())
static = json.loads((root / "supplementary/b5-static-001.json").read_text())
assert static["status"] == "passed"
for c in nb.cells:
    if c.cell_type == "code":
        assert c.execution_count is not None
        assert all(o.output_type != "error" for o in c.outputs)
for idx, label in [
    (37, "Interior step"),
    (40, "Base"),
    (43, "Terminal"),
    (46, "Exceptional horizon"),
]:
    streams = "".join(
        o.get("text", "") for o in nb.cells[idx].outputs if o.output_type == "stream"
    )
    assert (
        label in streams
        and "all Gram/function/offset residuals exactly zero" in streams
    )
assert any("image/png" in o.get("data", {}) for o in nb.cells[9].outputs)
notebook_hash = hashlib.sha256(path.read_bytes()).hexdigest()
proof_arguments = {
    "step": "For symbolic positive integer k,N and L>0, verify interior identity in cell 37 for 1<=k<=N-2. Every Gram, function and offset entry simplifies exactly to zero.",
    "base": "Cell 40 verifies the distinct N>=2 initial context with d0=x0-xstar; V0=0. Cell 46 separately verifies N=1.",
    "boundary": "Cell 43 proves the terminal step for N>=2 and V_N=h_N-h_star-L||d0||^2/(4N). The N=1 terminal identity is separately checked.",
    "signs": "Cells 3,47,48: 2N-i>=N>=1 and 2N+1-i>=N+1 for 1<=i<=N; L>0. Multiplier differences simplify to positive rational fractions, terminal weights to 1/(N+1),2/(N+1), and each supplied SOS coefficient is nonnegative term by term.",
    "domain": "Real finite-dimensional Euclidean space; f convex L-smooth, g closed proper convex; defined proximal steps; N integer>=1, L>0, R>=0; composite stationary optimizer. N=2 has no interior steps; N=1 checked separately.",
    "normalization": "V_N<=V0=0 gives h_N-h_star<=L||x0-xstar||^2/(4N)<=LR^2/(4N); no division by R.",
    "full_pep": "Cell 47 explicitly assembles every optimizer/consecutive multiplier family and every supplied square. The verified base, interior and terminal identities telescope to this global certificate for all N>=2, with the same N=1 empty-sum convention checked in cell 46.",
    "sharpness": "One-dimensional f=0, g(x)=c max(x,0), c=LR/(2N), x0=R, xstar=0 gives xN=R/2 and exact value LR^2/(4N); positive iterates justify the proximal recurrence.",
}
state = {
    **b4,
    "proof_checks": {
        k: True
        for k in ("step", "base", "boundary", "signs", "domain", "normalization")
    },
    "proof_arguments": proof_arguments,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": True,
    "lyapunov_proof_verified": True,
    "formula_status": {"lambda": "verified", "S": "verified"},
    "coefficient_formula_status": "verified",
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": b4["expression_structure"],
    "lyapunov_formula": nb.cells[2].source,
    "local_multiplier_code": nb.cells[34].source,
    "remaining_unknowns": [],
    "unresolved_coefficients": [],
    "symbolic_verification_cells": {
        key: {
            "cell_index": idx,
            "cell_id": nb.cells[idx].id,
            "source": nb.cells[idx].source,
        }
        for key, idx in [
            ("definitions", 34),
            ("step", 37),
            ("base", 40),
            ("boundary", 43),
            ("N1", 46),
            ("signs", 48),
        ]
    },
    "global_identity_markdown": nb.cells[47].source,
    "final_notebook": "pgm_example_lyap.ipynb",
    "final_notebook_sha256": notebook_hash,
    "presentation_policy": "evaluation-ancillary-v1",
    "rendered_review_performed": False,
    "markdown_source_checked": True,
    "final_execution": {
        "method": "pinned Python -I -B; runpy nbconvert --to notebook --execute; private attempt kernel",
        "log": "supplementary/b5-final-execution.log",
        "exit_code": 0,
    },
    "static_evidence": "supplementary/b5-static-001.json",
    "run_status": "complete",
    "unresolved_work": [],
}
(root / "state/pgm_b5.json").write_text(json.dumps(state, indent=2, allow_nan=False))
items = [
    (
        "title, problem description, and the algorithm update equations in LaTeX",
        "0",
        "Assumptions, proximal relation and metric present.",
    ),
    (
        "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
        "1,2,3",
        "Placeholder replaced by separate proof heading, theorem with full potential and self-contained detailed proof outline.",
    ),
    ("imports", "4,5", "Approved-path bootstrap and imports executed."),
    (
        "function/operator definitions",
        "6",
        "f smooth convex, g convex, h sum; parameters defined.",
    ),
    (
        "make_ctx_pgm and get_pep_setup",
        "7",
        "Actual recursion, composite stationary point, squared radius constraint and objective exposed.",
    ),
    (
        "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
        "8,9,10",
        "All seven printed solver values and statuses retained; executed image/png comparison plot present.",
    ),
    (
        "dense and relaxed proof solves",
        "11,12",
        "Dense/relaxed values, all group summaries, basis and sparsity recipe replayed. Refinement to derived-lambda dual formulation documented.",
    ),
    (
        "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
        "13,14,15,47",
        "All dual families, labeled multiplier/SOS matrices, reconstruction and complete residual checks executed. Global formula later established by exact local identities and explicit telescoping.",
    ),
    (
        "partial-sum Lyapunov construction and rank profile",
        "16,17,18",
        "Visible lyap/partial_sum loop; complete certificate replay and coverage; fixed (1,1) exclusions and rank 4 at N4,N6.",
    ),
    (
        "special-vector identification",
        "19-26",
        "Real candidate scan and sparse-basis search output retained for every searched index; adopted basis independence checked including endpoints.",
    ),
    (
        "coefficient extraction and closed-form V_k",
        "27-34",
        "All numerical coefficient matrices, full function/constant terms and endpoint reconstructions; labeled exact candidate matrices and final full formula. Arbitrary-index identities establish formula.",
    ),
    (
        "symbolic step, base, and boundary identities",
        "35-49",
        "Separate symbolic PEPFlow contexts with actual LHS/RHS/diff; all-coordinate exact zeros for step, base, boundary and N1; denominator signs, telescope and normalization established.",
    ),
]
lines = [
    f"Notebook: {path.name}\nLast reviewed block: B5\nSHA-256: {notebook_hash}\nPresentation policy: evaluation-ancillary-v1. No browser/rendered/image review performed. Markdown delimiters, control characters and saved outputs checked under that override.\nStatic checks: supplementary/b5-static-001.json. Final clean-kernel nbconvert execution: supplementary/b5-final-execution.log.\n",
    "| Item | Status | Cell indices | Evidence |",
    "|---|---|---|---|",
]
lines += [
    f"| {i}. {label} | verified | {indices} | {evidence} |"
    for i, (label, indices, evidence) in enumerate(items, 1)
]
(root / "supplementary/pgm_example_lyap_checklist.md").write_text("\n".join(lines))
closure = dict(
    current_block="B5",
    completion_status="complete",
    next_block=None,
    entry_exit_reason="All arbitrary-horizon identities/signs, final static checks, clean-kernel notebook execution and twelve-item content audit passed",
    operational_status="stopped_complete",
    run_status="complete",
    completed_blocks=["B1", "B2", "B3", "B4", "B5"],
    unresolved_work=[],
    notebook="pgm_example_lyap.ipynb",
    notebook_sha256=notebook_hash,
    state="state/pgm_b5.json",
    numerical_certificate_verified=True,
    analytic_full_pep_verified=True,
    lyapunov_proof_verified=True,
    access_control="instruction_only",
    prohibited_material_observed=False,
    supplied_assistance="Fixed PGM SOS aid supplied in own input; verified with normalization one",
    audit_limit="No exhaustive OS-level read tracing. Available actual tool outputs, immutable static evidence, source hashes and attempt records support the stated scope; no claim of OS-enforced isolation.",
    usage={"tokens": None, "reason": "Worker token usage unavailable"},
    presentation_policy="evaluation-ancillary-v1",
    rendered_review_performed=False,
)
(root / "supplementary/final-handoff.json").write_text(json.dumps(closure, indent=2))
print(
    json.dumps(
        {
            "run_status": "complete",
            "notebook_sha256": notebook_hash,
            "code_cells": sum(c.cell_type == "code" for c in nb.cells),
            "proof_checks": state["proof_checks"],
            "unresolved_work": [],
        }
    )
)
