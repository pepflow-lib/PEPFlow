"""Audit the final executed notebook and record the established theorem/status."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
notebook_path = ROOT / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(notebook_path, as_version=4)
b4 = json.loads((ROOT / "state/dual_feg_b4.json").read_text())
static = json.loads((ROOT / "supplementary/b5-static-001.json").read_text())
execution = json.loads((ROOT / "supplementary/b5-nbconvert-execution.json").read_text())
exact = json.loads((ROOT / "supplementary/b5-exact-checks.json").read_text())
assert (
    static["status"] == "passed"
    and execution["status"] == "passed"
    and execution["returncode"] == 0
)
digest = hashlib.sha256(notebook_path.read_bytes()).hexdigest()
assert digest == execution["sha256"]
assert len(exact) == 6 and all(
    all(item[k] is True for k in ["gram_zero", "function_zero", "offset_zero"])
    for item in exact.values()
)
outputs = "\n".join(record["text"] for record in execution["streams"])
assert outputs.count("Gram/function/offset residuals are exactly zero") == 6
assert "Theorem: ||A(x_N)||^2 <= 4 L^2 R^2 / N^2" in outputs
assert execution["plot_count"] >= 1
heading_positions = {
    cell.source.splitlines()[0]: i
    for i, cell in enumerate(nb.cells)
    if cell.cell_type == "markdown" and cell.source.startswith("#")
}
assert (
    heading_positions["## Proof Statement"]
    < heading_positions["### Theorem"]
    < heading_positions["### Proof outline"]
)
assert all(c.execution_count is not None for c in nb.cells if c.cell_type == "code")
assert not any(o.output_type == "error" for c in nb.cells for o in c.get("outputs", []))
for c in nb.cells:
    if c.cell_type == "markdown":
        assert not any(
            x in c.source for x in ["\x0c", "\r", "\\(", "\\)", "\\[", "\\]"]
        )
latex_output_cells = [
    i
    for i, c in enumerate(nb.cells)
    if any("text/latex" in o.get("data", {}) for o in c.get("outputs", []))
]
math_output_count = sum(
    "text/latex" in o.get("data", {}) for c in nb.cells for o in c.get("outputs", [])
)
assert math_output_count >= 10
for name in ["step", "base", "terminal_step", "N1", "boundary"]:
    matching = [
        i
        for i, c in enumerate(nb.cells)
        if f'exact_checks["{name}"] = verify_exact' in c.source
    ]
    assert len(matching) == 1 and matching[0] in latex_output_cells
formula = "V0=0; for 1<=k<N: Vk=-(4L/N)<gN,x0-xN>+(4L/(N-k))<gN,xk-xN>-4<gN,zk>+(4L/(N-k))<xk-xN,zk>-2||zk||^2; VN=2||gN||^2-(4L/N)<gN,x0-xN>; gN=A(xN)."
arguments = {
    "step": "For m=N-k>=2, Vk+1-Vk=4L/[m(m-1)] M_k+2/m^2 Q_k. Verified symbolically with m=q+1, q a positive integer, arbitrary positive L and symbolic N. All scalar components vanish.",
    "base": "For every N>=2, z0=0 gives V0=0 and the first-step identity with multipliers 4L/[N(N-1)],2/N^2. The separate N=1 check establishes V1=2Q0.",
    "boundary": "The terminal update gives VN-VN-1=2Q_N-1. Separately, gN^2-4L^2R^2/N^2=VN+(4L/N)Mstar-S+(4L^2/N^2)(||x0-xstar||^2-R^2), with S=||(2L/N)(x0-xstar)-gN||^2.",
    "signs": "Monotonicity makes M_k,Mstar nonpositive; Lipschitz continuity makes Q_k nonpositive. Multipliers are positive for L>0,N>=1,m>=2, and S is a squared norm. Therefore all increments are nonpositive and all normalized boundary terms have the required direction.",
    "domain": "Real finite-dimensional Euclidean space; monotone L-Lipschitz A; L>0; R>=0; integer N>=1; A(xstar)=0; radius bound and z0=0. All denominators are positive in their stated domains. No division by R or residual norm is used.",
    "normalization": "The exact boundary identity retains the squared radius R^2. VN<=V0=0 and each remaining right-hand term <=0 yield ||A(xN)||^2<=4L^2R^2/N^2, including N=1 and R=0.",
    "global_full_pep": "Sum the exact first/interior/terminal identities to replace VN by sum_{k=0}^{N-2}(4L/[(N-k)(N-k-1)] M_k+2/(N-k)^2 Q_k)+2Q_N-1. Substitution into the exact normalized boundary identity gives the displayed complete global certificate with star multiplier4L/N, radius multiplier4L^2/N^2 and square S. Empty sum for N=1. This is a symbolic telescoping derivation for arbitrary N, not a finite-sample fit.",
}
structure = {**b4["expression_structure"]}
for name in ["initial", "interior", "terminal"]:
    structure[name] = dict(structure[name])
    structure[name]["verified_formula"] = structure[name].pop("coefficient_candidate")
local_code = 'def local_multipliers(k, N, L):\n    if k == N-1:\n        return {"Lipschitz": 2}\n    m = N-k\n    return {"monotonicity": 4*L/(m*(m-1)), "Lipschitz": 2/m**2}\n'
state = {
    **b4,
    "proof_checks": {
        name: True
        for name in ["step", "base", "boundary", "signs", "domain", "normalization"]
    },
    "proof_arguments": arguments,
    "exact_component_checks": exact,
    "lyapunov_formula": formula,
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": structure,
    "local_multiplier_code": local_code,
    "coefficient_formula_status": "verified",
    "formula_status": {"lambda": "verified", "S": "verified"},
    "unresolved_coefficients": [],
    "remaining_unknowns": [],
    "remaining_analytic_obligations": [],
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": True,
    "lyapunov_proof_verified": True,
    "theorem": "For every integer N>=1, ||A(x_N)||^2 <= 4 L^2 R^2/N^2 under the supplied assumptions and alpha=1/L.",
    "notebook": "dual_feg_example_lyap.ipynb",
    "notebook_sha256": digest,
    "final_static_evidence": "supplementary/b5-static-001.json",
    "final_execution_evidence": "supplementary/b5-nbconvert-execution.json",
    "presentation_policy": "evaluation-ancillary-v1",
    "rendered_review": "not performed; explicitly omitted by frozen policy",
    "run_status": "completed",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "unresolved_work": [],
}
(ROOT / "state/dual_feg_b5.json").write_text(
    json.dumps(state, indent=2, allow_nan=False)
)
checklist = ROOT / "supplementary/dual_feg_example_lyap_checklist.md"
original_items = {}
for line in checklist.read_text(encoding="utf-8-sig").splitlines():
    parts = [part.strip() for part in line.split("|")]
    if len(parts) >= 6 and parts[1].isdigit():
        original_items[int(parts[1])] = parts[2]
assert set(original_items) == set(range(1, 13))


def indices(fragment, cell_type=None):
    return ",".join(
        str(i)
        for i, c in enumerate(nb.cells)
        if fragment in c.source and (cell_type is None or c.cell_type == cell_type)
    )


cells = {
    1: "0",
    2: f"{heading_positions['### Theorem']},{heading_positions['### Proof outline']}",
    3: indices("import matplotlib.pyplot"),
    4: indices("A = pf.LipschitzMonotoneOperator"),
    5: indices("def make_ctx_dual_feg"),
    6: indices("plt.plot"),
    7: indices('print("Dense optimum:')
    + ","
    + indices('print("Retained interpolation constraints:'),
    8: indices("Candidate multiplier error")
    + ","
    + indices("checks, certificate_ctx")
    + ","
    + indices("Candidate square Gram error"),
    9: indices("rank_samples = []"),
    10: indices("in_col_by_k = {}")
    + ","
    + indices("sparse_coefficients = {}")
    + ","
    + indices("def V_k_basis(k)"),
    11: indices("coefficients, reconstruction, fit_errors =")
    + ","
    + str(heading_positions["### Closed-form potential"]),
    12: ",".join(
        indices('exact_checks["' + name + '"]')
        for name in ["step", "base", "terminal_step", "N1", "boundary"]
    ),
}
evidence_text = {
    1: "Assumptions, selected metric and all recurrence equations inspected in saved Markdown.",
    2: "Separate theorem and self-contained proof outline include full potential, residual families, signs, endpoints and exact rate.",
    3: "Pinned-source imports executed in fresh kernel.",
    4: "Monotone Lipschitz operator and symbolic parameters present and executed.",
    5: "Visible exact-ratio algorithm, z0, zero point, squared radius and final-residual metric executed.",
    6: "N=1..7 cached numeric values and comparison curve printed; executed PNG plot retained; N=2 solver status disclosed.",
    7: "Dense and both sparse discovery solves retained; selected support and preserved optimum inspected; additional N6 sample verified.",
    8: "Actual lambda/S checks, full numerical LDL decomposition, true S and candidate displays, initial search, exact global telescoping argument inspected.",
    9: "Visible partial-sum loop, all contribution assignments, sign/coverage checks and same-recipe N4/N6 rank confirmation executed.",
    10: "Visible framework sparse-basis search with per-index outputs, adopted basis independence, every-index full-component reconstruction executed.",
    11: "Labeled numerical/candidate matrices and complete potential present; symbolic identities prove candidate coefficients for all claimed horizons.",
    12: "Separate symbolic step, base, terminal, N1 and radius-boundary checks execute; six exact Gram/function/offset checks pass; signs/domain/normalization proof inspected.",
}
header = f"Notebook: {notebook_path.name}\nLast reviewed block: B5\nSHA-256: {digest}\n\nPresentation policy: evaluation-ancillary-v1. Rendering/image inspection was not performed and is not a completion gate. Source formulas, all execution outputs, plot presence, Markdown delimiters and control characters were checked.\n\n| Item | Requirement | Status | Cell indices | Evidence |\n|---|---|---|---|---|\n"
rows = [
    f"| {i} | {original_items[i]} | verified | {cells[i]} | {evidence_text[i]} |"
    for i in range(1, 13)
]
checklist.write_text(header + "\n".join(rows))
closure = dict(
    current_block="B5",
    completion_status="complete",
    next_block=None,
    entry_exit_reason="Exact theorem and global certificate established; required final static, nbconvert, and notebook-content checks passed",
    operational_status="stopped_completed",
    run_status="completed",
    completed_blocks=state["completed_blocks"],
    unresolved_work=[],
    deadline_utc="2026-09-23T21:04:02.221276+00:00",
    finished_utc=datetime.now(timezone.utc).isoformat(),
    access_control="instruction_only",
    prohibited_sources_observed=False,
    source_records=[
        "supplementary/preflight-consulted-sources.json",
        "supplementary/b1-access-and-recovery.json",
        "supplementary/b2-handoff-and-access.json",
        "supplementary/b3-revisit-b2-handoff.json",
        "supplementary/b2-N6-handoff.json",
        "supplementary/b3-handoff.json",
        "supplementary/b4-handoff.json",
    ],
    B5_approved_reads=[
        "supplementary/approved/plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md",
        "supplementary/approved/pepflow/utils.py",
        "supplementary/approved/pepflow/parameter.py",
    ],
    own_generated_reads="Own setup, notebook, helper and verifier sources, state files and evidence artifacts named by the block records and commands",
    operational_repairs=[
        "Broad-helper Windows path-length staging error repaired with narrow attempt-owned helper root and repeated preflight",
        "Nullable dual conversion type narrowing repaired and coherent certificate reacquired",
        "Notebook LaTeX escape repaired",
        "Reconstruction parameter dictionary taken from saved certificate",
        "Symbolic display converted from list to NumPy array as required by pprint_labeled_matrix",
        "Closure audit corrected to count matrix outputs rather than output-bearing cells; actual notebook has 20 LaTeX outputs",
        "One empty apply_patch with a mistyped nonexistent path was rejected during patch validation; no content read or write occurred",
    ],
    operational_warnings=[
        "N2 initial sweep optimal_inaccurate, disclosed; selected and confirming certificates optimal",
        "Context-name reuse warnings during explicit fresh context rebuilds",
        "Nonblocking Windows ZMQ selector-thread warning",
        "nbconvert dash comm-target warning, with successful notebook execution",
    ],
    audit_limit="Instruction-only isolation; resolution probes and source manifests do not exhaustively trace filesystem reads or model training exposure",
    exports_performed=False,
    notebook_sha256=digest,
    token_usage=None,
)
(ROOT / "supplementary/final-closure.json").write_text(json.dumps(closure, indent=2))
print(
    json.dumps(
        {
            "run_status": closure["run_status"],
            "finished_utc": closure["finished_utc"],
            "notebook_sha256": digest,
            "cell_count": len(nb.cells),
            "plot_count": execution["plot_count"],
            "labeled_math_output_cells": latex_output_cells,
            "exact_identity_count": 6,
            "proof_statuses": {
                k: state[k]
                for k in [
                    "numerical_certificate_verified",
                    "analytic_full_pep_verified",
                    "lyapunov_proof_verified",
                ]
            },
            "headings": heading_positions,
            "unresolved_work": [],
        },
        indent=2,
    )
)
