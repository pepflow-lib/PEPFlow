import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd().resolve()
nbpath = root / "feg_example_lyap.ipynb"
nb = json.loads(nbpath.read_text())
static = json.loads((root / "supplementary/b5-static-002.json").read_text())
execution = json.loads((root / "supplementary/b5-final-execution.json").read_text())
assert static["status"] == "passed" and execution["returncode"] == 0
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        assert cell["execution_count"] is not None
        assert not any(out["output_type"] == "error" for out in cell["outputs"])
    if cell["cell_type"] == "markdown":
        source = "".join(cell["source"])
        assert "\\(" not in source and "\\[" not in source
        assert not any(char in source for char in ("\r", "\x0c", "\x08"))
        assert source.count("$") % 2 == 0
for index, word in ((45, "Step"), (48, "Base"), (51, "Boundary")):
    outputs = nb["cells"][index]["outputs"]
    text = "".join("".join(o.get("text", [])) for o in outputs)
    assert word + " function coordinates: Matrix(0, 0, []) offset: 0" in text
    assert any("text/latex" in o.get("data", {}) for o in outputs)
assert any("image/png" in o.get("data", {}) for o in nb["cells"][9]["outputs"])
b4 = json.loads((root / "state/feg_b4.json").read_text())
proof_checks = {
    key: True
    for key in ("step", "base", "boundary", "signs", "domain", "normalization")
}
proof_arguments = {
    "step": "Symbolic PEPFlow recurrence in notebook cells 39 and 45 verifies every Gram/function/offset coefficient; multipliers 2(k+1)^2/N^2 and 4Lk(k+1)/N^2 are positive for L>0, N>=1, 1<=k<N.",
    "base": "Separate shared-point initial context in cell 48 proves V1=2*Lip1/N^2<=0=V0. No independent half-step evaluation is introduced.",
    "boundary": "Cell 51 proves residual-bound=V_N+(4L/N)*MonStar+(4L^2/N^2)*(||x0-xstar||^2-R^2)-||A_N-(2L/N)*(x0-xstar)||^2. Each right-hand term is nonpositive after telescoping.",
    "domain": "Real finite-dimensional Euclidean space, monotone L-Lipschitz A, L>0, R>=0, integer N>=1. Interior k=1..N-1; N=1 has an empty interior. Denominators L,N,k,k+1 are nonzero where used. No division by R or a residual.",
    "signs": "Lipschitz and monotonicity residuals are <=0 by assumptions; initial residual <=0; square >=0. Coefficients listed in notebook cell 52 are positive, so V is nonincreasing and the terminal square is subtracted.",
    "normalization": "Coefficient recurrence a(k+1)/(k+1)^2=a(k)/k^2 and terminal a(N)=2 give a=2k^2/N^2,b=2Lk/N^2,c=0; terminal identity yields exactly 4L^2R^2/N^2.",
}
resolved_case = {
    "basis_labels": ["A(x_k)", "x_k-x_0"],
    "quadratic_coefficients": {
        "C00": "2*k**2/N**2",
        "C01=C10": "2*L*k/N**2",
        "C11": "0",
    },
}
structure = {
    "quadratic_convention": "sum_ij Cij <vi,vj>, symmetric C; off-diagonal counted twice",
    "interior": {**resolved_case, "index_domain": "1<=k<=N-1"},
    "initial": {"index_domain": "k=0", "basis_labels": [], "value": "0"},
    "terminal": {**resolved_case, "index_domain": "k=N"},
    "function_terms": [],
    "constant_terms": [],
}
coeff_code = """def coeff_pattern(k, N, L=sp.S.One):
    if k == 0:
        return sp.zeros(0, 0)
    return sp.Matrix([[2*sp.S(k)**2/sp.S(N)**2, 2*L*sp.S(k)/sp.S(N)**2], [2*L*sp.S(k)/sp.S(N)**2, 0]])
"""
local_code = """def local_multipliers(k, N, L=sp.S.One):
    return {"Lipschitz": 2*(sp.S(k)+1)**2/sp.S(N)**2, "Monotone": 4*L*sp.S(k)*(sp.S(k)+1)/sp.S(N)**2}
"""
state = {
    **b4,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": True,
    "proof_checks": proof_checks,
    "proof_arguments": proof_arguments,
    "lyapunov_formula": "V_0=0; V_k=2*k**2/N**2*||A(x_k)||**2+4*L*k/N**2*<A(x_k),x_k-x_0>, 1<=k<=N",
    "theorem": "||A(x_N)||**2 <= 4*L**2*R**2/N**2 for every integer N>=1",
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": structure,
    "coeff_code": coeff_code,
    "local_multiplier_code": local_code,
    "coefficient_formula_status": "verified",
    "unresolved_coefficients": [],
    "proof_source": {
        name: (root / "supplementary" / name).read_text(encoding="utf-8-sig")
        for name in ("b5_derivation.py", "b5_step.py", "b5_base.py", "b5_boundary.py")
    },
    "final_notebook_sha256": hashlib.sha256(nbpath.read_bytes()).hexdigest(),
    "final_execution_evidence": "supplementary/b5-final-execution.json",
    "final_static_evidence": "supplementary/b5-static-002.json",
    "presentation_policy": "evaluation-ancillary-v1",
    "visual_review_performed": False,
    "run_status": "completed",
    "remaining_required_work": [],
    "remaining_separate_objectives": [
        "Global analytic identification of the numerical dual table not claimed; require_analytic_full_pep=false."
    ],
}
(root / "state/feg_b5.json").write_text(json.dumps(state, indent=2, allow_nan=False))
items = [
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
    "0: assumptions, metric, both algorithm equations and shared first half-step inspected",
    "1-3: separate Proof Statement, Theorem with potential and bound, self-contained proof outline with base/step/boundary equations",
    "4-5: private approved-root bootstrap and executed imports",
    "6: L,R and LipschitzMonotoneOperator",
    "7: actual recurrence, tags, shared initial point, squared radius and metric",
    "8-10: seven printed SDP values, curve and embedded PNG present; no image inspection under presentation override",
    "11-12: dense and sparse solves, basis, both multiplier families, S eigenvalues and preserved objective",
    "13-18: complete selected numerical identity, true S and LDL matrices, reconstruction residuals, initial formula search and honest candidate mismatch/global status",
    "19-23: certificate reconstruction, whole-S decomposition, visible partial-sum loop and ranks, both-horizon coverage and fixed exclusions",
    "24-32: real candidate/filter/sparse search with all-index selected bases, zero counts and adopted basis",
    "33-42: all numerical matrices and full-component reconstruction; unknown coefficient recurrence solved exactly; labeled exact coefficients and numerical differences; closed-form conclusion",
    "43-52: separate symbolic PF step/base/boundary contexts, exact zero Gram/function/offset outputs, LaTeX equations and signs/domain/normalization argument",
]
lines = [
    f"# Notebook evidence checklist\nNotebook: {nbpath.name}\nLast reviewed block: B5\nSHA-256: {state['final_notebook_sha256']}\nPresentation: evaluation-ancillary-v1; source math and outputs inspected, no rendering or image inspection performed.\n",
    "| Item | Status | Cells and evidence |",
    "|---|---|---|",
]
lines += [
    f"| {i}. {item} | verified | {ev} |"
    for i, (item, ev) in enumerate(zip(items, evidence), 1)
]
(root / "supplementary/feg_example_lyap_checklist.md").write_text("\n".join(lines))
closure = {
    "current_block": "B5",
    "completion_status": "complete",
    "next_block": None,
    "entry_exit_reason": "Exact local Lyapunov proof, final required static checks, Jupyter nbconvert clean-kernel execution and twelve-item content audit completed",
    "operational_status": "finished",
    "run_status": "completed",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "unresolved_required_work": [],
    "unresolved_separate_claim": "No global analytic identification of the selected numerical dual table claimed; not a required objective",
    "original_deadline_utc": "2026-09-23T22:53:27.110234+00:00",
    "closed_utc": datetime.now(timezone.utc).isoformat(),
    "source_records": [
        "supplementary/preflight-access-001.json",
        "supplementary/b1-handoff.json",
        "supplementary/b2-handoff.json",
        "supplementary/b3-handoff-001.json",
        "supplementary/b2-handoff-N4.json",
        "supplementary/b3-handoff-003.json",
        "supplementary/b4-handoff.json",
    ],
    "B5_consulted_sources": [
        "supplementary/approved/plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md",
        "supplementary/approved/pepflow/parameter.py",
        "state/feg_b4.json",
        "own generated B5 scripts, notebook, execution and static evidence",
    ],
    "commands": "Pinned Python -I -B executing run_b5.py, build_b5_notebook.py, repair_b5_typing.py, execute_final_notebook.py, finalize_b5.py; exact static adapter subprocesses in b5-static evidence and final Jupyter nbconvert argv in b5-final-execution.json",
    "incidents": [
        "SymPy dynamic Function factory needed a Callable type annotation via cast; runtime symbolic expressions unchanged; required static check rerun and passed.",
        "Final execution emitted Windows ZMQ selector fallback and missing dash comm handler warnings; execution completed without cell errors.",
    ],
    "access_control": "instruction_only",
    "prohibited_sources_used_or_encountered": False,
    "integrity_exceptions": [],
    "audit_limit": "Tool/source manifests record available evidence, not an exhaustive OS-level filesystem read audit. No claims about model-training knowledge.",
    "presentation_policy": "evaluation-ancillary-v1; no browsing, rendering, image inspection, or exports",
    "token_usage": None,
    "final_notebook_sha256": state["final_notebook_sha256"],
}
(root / "supplementary/b5-handoff.json").write_text(json.dumps(closure, indent=2))
print(
    json.dumps(
        {
            "run_status": "completed",
            "proof_checks": proof_checks,
            "notebook_sha256": state["final_notebook_sha256"],
            "closed_utc": closure["closed_utc"],
        },
        indent=2,
    )
)
