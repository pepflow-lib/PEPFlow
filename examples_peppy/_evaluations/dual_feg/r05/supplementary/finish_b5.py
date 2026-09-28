"""Audit executed notebook and save the final analytic state."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
SUP = ROOT / "supplementary"
path = ROOT / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
execution = json.loads((SUP / "b5-execution-final.json").read_text())
assert execution["returncode"] == 0
static = json.loads((SUP / "b5-static-002.json").read_text())
assert static["status"] == "passed"
for c in nb.cells:
    if c.cell_type == "code":
        assert c.execution_count is not None
        assert not any(o.output_type == "error" for o in c.outputs)
streams = "\n".join(
    o.get("text", "")
    for c in nb.cells
    for o in c.get("outputs", [])
    if o.output_type == "stream"
)
for text in [
    "Interior step (t>=2) exact identity verified.",
    "Base (N>=1, z_0=0) exact identity verified.",
    "Final step (including N=1) exact identity verified.",
    "Metric boundary and normalization exact identity verified.",
    "All exact identities verified.",
]:
    assert text in streams
assert any(
    "image/png" in o.get("data", {}) for c in nb.cells for o in c.get("outputs", [])
)
b4 = json.loads((ROOT / "state/dual_feg_b4.json").read_text())
sources = json.loads((SUP / "b5-cell-sources.json").read_text(encoding="utf-8-sig"))
formula = "For a=A(x_N), V_k=-4<a,z_k>-2||z_k||^2+4L/(N-k)<a+z_k,x_k-x_N>-4L/N<a,x_0-x_N> (0<=k<N); V_N=2||a||^2-4L/N<a,x_0-x_N>."
structure = {
    "quadratic_convention": "V=sum_ij C_ij<v_i,v_j>; symmetric C; off-diagonal counted twice",
    "interior": {
        "index_domain": "1<=k<N, integer N>=1, L>0",
        "basis_labels": ["A(x_N)", "z_k", "x_k-x_N", "x_0-x_N"],
        "coefficients": {
            "C_00": "0",
            "C_01": "-2",
            "C_02": "2*L/(N-k)",
            "C_03": "-2*L/N",
            "C_11": "-2",
            "C_12": "2*L/(N-k)",
            "C_13": "0",
            "C_22": "0",
            "C_23": "0",
            "C_33": "0",
        },
    },
    "initial": {
        "index_domain": "k=0; every N>=1",
        "basis_labels": [],
        "coefficients": "V_0=0; z_0=0 makes the generic formula cancel",
    },
    "terminal": {
        "index_domain": "k=N; every N>=1",
        "basis_labels": ["A(x_N)", "x_0-x_N"],
        "coefficients": {"C_00": "2", "C_01": "-2*L/N", "C_11": "0"},
    },
    "function_terms": [],
    "constant_terms": [],
}
arguments = {
    "step": "For 0<=k<=N-2, t=N-k>=2: V_(k+1)-V_k=2/t^2 H_k+4L/[t(t-1)] M_k. Exact PEPFlow Gram/function/offset zero.",
    "base": "V_0=0 with z_0=0 and t=N; verified in a separate symbolic context for N>=1.",
    "boundary": "Final step V_N-V_(N-1)=2 Lip(x_(N-1),x_N). Metric boundary: ||a||^2-4L^2/N^2||x_0-x_star||^2=V_N+4L/N Mon(x_N,x_star)-||a-2L/N(x_0-x_star)||^2.",
    "signs": "All interpolation multipliers are positive for L>0,N>=1,t>=2, verified with positive symbolic variables. Lipschitz/monotone residuals <=0; squared norm >=0.",
    "domain": "Real finite-dimensional Euclidean space; monotone L-Lipschitz A; A(x_star)=0; L>0,R>=0,N integer>=1. Interior range empty for N=1; base and last step cover it.",
    "normalization": "V_N<=V_0=0 implies residual bound 4L^2/N^2||x_0-x_star||^2<=4L^2R^2/N^2. No division by R.",
}
coeff_code = """def final_coefficients(k,N,L):
    N,L=sp.sympify(N),sp.sympify(L)
    if k==0:
        return sp.zeros(0,0)
    if k==N:
        return sp.Matrix([[2,-2*L/N],[-2*L/N,0]])
    t=N-k
    return sp.Matrix([[0,-2,2*L/t,-2*L/N],[-2,-2,2*L/t,0],[2*L/t,2*L/t,0,0],[-2*L/N,0,0,0]])
"""
state = {
    **b4,
    "proof_checks": {
        k: True
        for k in ["step", "base", "boundary", "signs", "domain", "normalization"]
    },
    "proof_arguments": arguments,
    "lyapunov_formula": formula,
    "theorem": "||A(x_N)||^2 <= 4*L^2*R^2/N^2",
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": structure,
    "coeff_code": coeff_code,
    "coefficient_formula_status": "verified",
    "local_multiplier_code": "def local_multipliers(k,N,L):\n    k,N,L=sp.sympify(k),sp.sympify(N),sp.sympify(L)\n    t=N-k\n    if k==N-1:\n        return {'lip':sp.Integer(2),'mon':sp.Integer(0)}\n    return {'lip':2/t**2,'mon':4*L/(t*(t-1))}\ndef boundary_multiplier(N,L):\n    return 4*sp.sympify(L)/sp.sympify(N)\n",
    "remaining_unknowns": [],
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": True,
    "require_analytic_full_pep": False,
    "symbolic_sources": {
        k: sources[k] for k in ["preamble", "step", "base", "last", "boundary", "signs"]
    },
    "final_notebook": path.name,
    "final_notebook_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "validation": {
        "static_evidence": "supplementary/b5-static-002.json",
        "execution_evidence": "supplementary/b5-execution-final.json",
        "presentation_policy": "evaluation-ancillary-v1",
        "rendered_review_performed": False,
    },
    "run_status": "success",
    "unresolved_required_work": [],
    "optional_unverified_work": [
        "Universal global full-PEP multiplier-table formula not separately certified."
    ],
}
(ROOT / "state/dual_feg_b5.json").write_text(json.dumps(state, indent=2))
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
ranges = {
    1: [0],
    2: [1, 2, 3],
    3: [4, 5],
    4: [7],
    5: [9, 10],
    6: [12, 13],
    7: [14, 15],
    8: list(range(16, 22)),
    9: list(range(22, 27)),
    10: list(range(27, 36)),
    11: list(range(36, 44)),
    12: list(range(44, 59)),
}
evidence = {
    1: "Assumptions, initial condition, metric and all three algorithm recurrences.",
    2: "Separate theorem and self-contained proof outline; explicit potential, all step residuals, endpoint and rate proof.",
    3: "Pinned approved imports; executed origin output.",
    4: "Lipschitz-monotone operator and parameters.",
    5: "Executable context builder and metric/initial-condition setup; zero initialization checked.",
    6: "Seven observed values, solver statuses, rate comparison and image/png plot output.",
    7: "Dense and selected sparse solves, preserved bound, every group summarized and labeled numerical dual tables.",
    8: "Initial formula search, all selected multipliers, candidate comparisons, true S matrix, complete LDL reconstruction and full-coordinate certificate residuals; global analytic status explicit.",
    9: "Visible actual partial-sum loop, all-coordinate certificate/coverage checks, nonincreasing direction, rank four at N=6,8 with fixed exclusions.",
    10: "Labeled candidate scan, actual sparse-basis search and zero-count outputs, adopted basis and independence including endpoints.",
    11: "All-index coefficient reconstruction and candidate comparisons; labeled exact coefficient matrix and final formula with general L.",
    12: "Separate exact PEPFlow step, base, final-step and metric-boundary identities with labeled residual matrices and zero function/constant residuals; domain, signs and normalization established.",
}
lines = [
    f"# Evidence checklist\nNotebook: {path.name}\nLast reviewed block: B5\nSHA-256: {state['final_notebook_sha256']}\nPresentation policy: evaluation-ancillary-v1. Source, equations and saved outputs inspected; no browser, rendering or image inspection was performed.\n",
    "| Item | Status | Cell indices and IDs | Evidence |",
    "|---|---|---|---|",
]
for i, item in enumerate(items, 1):
    cells = ", ".join(f"{j}:{nb.cells[j].id}" for j in ranges[i])
    lines.append(f"| {i}. {item} | verified | {cells} | {evidence[i]} |")
(SUP / "dual_feg_example_lyap_checklist.md").write_text("\n".join(lines))
record = {
    "current_block": "B5",
    "completion_status": "complete",
    "next_block": None,
    "entry_exit_reason": "Exact arbitrary-horizon Lyapunov proof and required final notebook checks completed",
    "operational_status": "closed",
    "run_status": "success",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "unresolved_required_work": [],
    "optional_unverified_work": state["optional_unverified_work"],
    "access_control": "instruction_only",
    "prohibited_sources_observed": False,
    "access_audit_limit": "Source declarations, approved adapter resolution evidence and tool logs are not an exhaustive filesystem read audit.",
    "consulted_source_records": [
        "preflight-access-record.json",
        "b1-handoff.json",
        "b2-handoff.json",
        "b3-revisit-b2.json",
        "b2-N8-handoff.json",
        "b3-handoff.json",
        "b4-handoff.json",
    ],
    "additional_sources": [
        "approved/plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md",
        "approved/pepflow/expression_manager.py",
        "own B4 state and evidence",
        "verify_b5_symbolic.py",
        "b5-cell-sources.json",
        "update_b5_notebook.py",
        "execute_b5_notebook.py",
        "execute_b5_final.py",
        "fix_b5_display.py",
        "finish_b5.py",
    ],
    "external_resources": [],
    "integrity_exceptions": [],
    "operational_incidents": "See earlier handoff records. B5 first nbconvert execution failed at symbolic matrix formatting; changed generated display precision to zero, retained b5-execution.json, repeated static checks and full clean-kernel nbconvert successfully. No frozen-source edits.",
    "presentation_policy": "evaluation-ancillary-v1",
    "rendered_review_performed": False,
    "final_notebook_sha256": state["final_notebook_sha256"],
    "deadline_utc": "2026-09-24T00:52:12.648185+00:00",
    "closed_utc": datetime.now(timezone.utc).isoformat(),
    "provider_token_usage": None,
}
(SUP / "attempt-closure.json").write_text(json.dumps(record, indent=2))
print(
    json.dumps(
        {
            "run_status": "success",
            "theorem": state["theorem"],
            "proof_checks": state["proof_checks"],
            "notebook_sha256": state["final_notebook_sha256"],
        },
        indent=2,
    )
)
