"""Persist final evidence from the already executed main notebook; no new proof claims."""

import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
supp = root / "supplementary"


def read(name):
    return json.loads((root / name).read_text(encoding="utf-8-sig"))


def write(name, value):
    (root / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


nbpath = root / "pgm_example_lyap.ipynb"
nb = read("pgm_example_lyap.ipynb")
execution = read("supplementary/b5-final-execution.json")
static = read("supplementary/b5-static-002.json")
digest = hashlib.sha256(nbpath.read_bytes()).hexdigest()
assert execution["returncode"] == 0
assert digest == execution["executed_notebook_sha256"]
assert static["status"] == "passed" and static["preflight_passed"]
streams = []
executed = []
images = []
for i, cell in enumerate(nb["cells"]):
    source = "".join(cell["source"])
    if cell["cell_type"] == "code":
        assert cell["execution_count"] is not None, i
        executed.append(i)
        for output in cell["outputs"]:
            assert output["output_type"] != "error", (i, output)
            streams.append("".join(output.get("text", [])))
            if "image/png" in output.get("data", {}):
                images.append(i)
    else:
        assert not any(ord(c) < 32 and c not in "\n\t" for c in source), i
        assert not any(s in source for s in [r"\(", r"\)", r"\[", r"\]"]), i
        assert len(re.findall(r"(?<!\\)\$", source)) % 2 == 0, i
assert 9 in images
output_text = "\n".join(streams)
checks_match = re.search(r"PROOF_CHECKS_JSON=(\{[^\n]+\})", output_text)
assert checks_match is not None
checks = json.loads(checks_match.group(1))
assert all(checks.values()) and len(checks) == 7
assert "Exact telescoping multiplier identities: [0, 0, 0, 0, 0]" in output_text
for phrase in [
    "Interior step, 1<=k<=N-2",
    "Base, N>=2",
    "Terminal, N>=2",
    "Single iteration, N=1",
    "Initial-distance normalization",
]:
    assert phrase + " exact zero: True" in output_text
b4 = read("state/pgm_b4.json")
state = copy.deepcopy(b4)
structure = copy.deepcopy(b4["expression_structure"])
structure["interior"]["coefficients"] = {
    "0,0": "-L/(4*N)",
    "0,1": "0",
    "0,2": "0",
    "0,3": "0",
    "1,1": "L*(N-k)/(2*N-k)**2",
    "1,2": "0",
    "1,3": "-1/(2*(2*N-k))",
    "2,2": "1/(2*L*(2*N-k))",
    "2,3": "0",
    "3,3": "0",
}
structure["terminal"]["coefficients"] = {"0,0": "-L/(4*N)"}
for term, formula in zip(
    structure["function_terms"], ["(k+1)/(2*N-k)", "k/(2*N-k)", "1", "1"]
):
    term["coefficient"] = formula
formula = {
    "notation": "r_k=x_k-x_star; a_k=grad f(x_k); F_k=f(x_k)-f(x_star); G_k=g(x_k)-g(x_star)",
    "initial": "V_0=0",
    "interior": "V_k=-L/(4*N)*||r_0||^2+L*(N-k)/(2*N-k)^2*||r_k||^2+||a_k-a_star||^2/(2*L*(2*N-k))-<r_k,a_k>/(2*N-k)+(k+1)/(2*N-k)*F_k+k/(2*N-k)*G_k, 1<=k<N",
    "terminal": "V_N=F_N+G_N-L/(4*N)*||r_0||^2",
    "rate": "h(x_N)-h(x_star)<=L*R^2/(4*N), N>=1",
}
symbolic = (supp / "b5_symbolic.py").read_text()
coeff = (supp / "b5_formula_check.py").read_text()
state.update(
    numerical_certificate_verified=True,
    analytic_full_pep_verified=True,
    lyapunov_proof_verified=True,
    proof_valid=True,
    proof_checks=checks,
    lyapunov_formula=formula,
    discovery_expression_structure=b4["expression_structure"],
    expression_structure=structure,
    coefficient_formula_status="verified",
    unresolved_coefficients=[],
    remaining_unknowns=[],
    rate_status="proved",
    coeff_code="import sympy as sp\n"
    + coeff[coeff.index("def coeff_pattern") : coeff.index("formula_comparisons =")],
    local_multiplier_code=symbolic,
    formula_status={"lambda": "verified", "S": "verified"},
    analytic_S_code=symbolic[: symbolic.index("# STEP")],
    proof_arguments={
        "step": "Exact full Gram/function/offset identity at symbolic k,N,L in notebook cell 50 for 1<=k<=N-2.",
        "base": "Exact separate base identity for N>=2, cell 53; V_0=0.",
        "boundary": "Exact separate terminal identity for N>=2, cell 56; N=1 exact identity in cell 59.",
        "signs": "Nonpositive convex interpolation residuals; all eleven square/interpolation/radius coefficients verified nonnegative using i=u+1,N=u+v+1 with integer u,v>=0 and L>0, cell 62.",
        "domain": "For 1<=i<=N, 2N-i>=N>=1 and 2N+1-i>=N+1. Interior 1<=k<N implies 2N-k>=N+1. No g(x_0) term is required; N=1 covered separately.",
        "normalization": "Exact metric-L*R^2/(4N)=V_N+L/(4N)*(||r_0||^2-R^2); radius constraint nonpositive and tau positive.",
        "global_full_pep": "Sum the exact base, interior and terminal identities, each residual and supplied S_i included once with its local coefficient, to obtain V_N=sum lambda I-sum S_i. Five exact multiplier telescope equations in cell 62 identify these coefficients with the global candidate. Add the exact radius normalization; no PSD or equality extras exist in this case.",
    },
    proof_evidence={
        "notebook_sha256": digest,
        "execution": "supplementary/b5-final-execution.json",
        "static": "supplementary/b5-static-002.json",
        "proof_cells": [50, 53, 56, 59, 62],
    },
    normalization_analytic={
        "tau": "L/(4*N)",
        "identity": "metric-L*R^2/(4*N)-tau*(||r_0||^2-R^2)-sum(lambda*I)+sum(S_i)=0",
    },
    presentation_policy="evaluation-ancillary-v1",
    rendering_performed=False,
)
state["global_multiplier_formula"] = {
    "initial_distance": "L/(4*N)",
    "f_star_0": "1/(2*N)",
    "f_star_i_interior": "(2*N+1)/((2*N-i)*(2*N+1-i)), 1<=i<N",
    "g_star_i_interior": "2*N/((2*N-i)*(2*N+1-i)), 1<=i<N",
    "f_star_N": "1/(N+1)",
    "g_star_N": "2/(N+1)",
    "f_consecutive_i": "i/(2*N+1-i), 1<=i<=N",
    "g_consecutive_i": "(i-1)/(2*N+1-i), 2<=i<=N",
    "other": "0",
    "N1": "f_star_0=f_star_1=f_0_1=1/2; g_star_1=1; tau=L/4",
}
write("state/pgm_b5.json", state)
checkpath = supp / "pgm_example_lyap_checklist.md"
old = checkpath.read_text()
requirements = [
    line.split("|")[2].strip()
    for line in old.splitlines()
    if re.match(r"\| \d+ \|", line)
]
assert len(requirements) == 12
locations = [
    "0",
    "1–3",
    "4–5",
    "6",
    "7",
    "8–10",
    "11–12",
    "13–21, 50–62",
    "22–27",
    "28–39",
    "40–47",
    "48–62",
]
evidence = [
    "Assumptions, metric, recurrence and inclusion checked as source.",
    "Final theorem states complete interior and endpoint potentials; proof outline includes residuals, SOS, local identities and convergence.",
    "Executed approved framework import and origin assertion.",
    "Smooth convex f, convex g, h=f+g and parameters.",
    "Executed context builder and setup definitions.",
    "Sweep and conjecture comparison printed; plot image output present, not viewed.",
    "Dense and sparse solve records, complete group summaries and preserved optimum.",
    "Numerical certificate checks and exact fixed-horizon checks retained; arbitrary-horizon identities and telescoping verify analytic lambda and supplied S.",
    "Full-coordinate coverage, PSD polar correction, same-certificate checks and ranks verified at N4/N6.",
    "Actual basis search, independence and all-index reconstruction outputs retained.",
    "Exact coefficient equations solved, endpoint anchor derived, formulas compared at every selected index and full closed form stated.",
    "Step, base, terminal, N=1 and radius identities exactly zero in all coordinates; sign/domain and telescoping obligations established.",
]
lines = [
    f"Notebook: {nbpath}",
    "Last reviewed block: B5",
    f"SHA-256: {digest}",
    "",
    "Presentation policy: evaluation-ancillary-v1. Source math delimiter/control-character checks passed. No rendering or image inspection performed; rendered review is waived by this evaluation policy.",
    "",
    "Final static adapter: passed (Ruff and ty). Final clean-kernel nbconvert execution: exit 0.",
    "",
    "| Item | Requirement | Status | Cells (zero-based) | Evidence |",
    "|---|---|---|---|---|",
]
lines += [
    f"| {i + 1} | {r} | verified | {locations[i]} | {evidence[i]} |"
    for i, r in enumerate(requirements)
]
checkpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
now = datetime.now(timezone.utc).isoformat()
audit = {
    "finished_utc": now,
    "notebook_sha256": digest,
    "executed_cells": executed,
    "error_outputs": 0,
    "plot_output_cells": images,
    "source_math_checks": "passed",
    "proof_checks": checks,
    "static_status": static["status"],
    "execution_returncode": 0,
    "access_control": "instruction_only",
    "audit_limit": "No exhaustive OS tracing",
    "prohibited_sources_observed": False,
    "source_records": [
        "preflight-access-record.json",
        "b1-handoff.json",
        "b2-handoff.json",
        "b3-partial-handoff.json",
        "b2-N6-handoff.json",
        "b3-handoff.json",
        "b4-partial-handoff.json",
        "b3-recovery-handoff.json",
        "b4-handoff.json",
    ],
    "B5_approved_consultations": [
        "dispatch.md",
        "input.md",
        "worker-protocol.md",
        "allowlist.json",
        "plugins/pepflow-workflows/skills/lyap-closed-form/SKILL.md",
        "plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md",
        "pepflow/function.py",
        "pepflow/parameter.py",
    ],
    "B5_own_sources": [
        "b5_symbolic.py",
        "b5_derivation.py",
        "b5_formula_check.py",
        "b5_final_checks.py",
        "build_b5_notebook.py",
        "run_final_notebook.py",
        "finalize_b5.py",
        "b5-static-001.json",
        "b5-static-002.json",
        "b5-final-execution.json",
    ],
    "operational_incidents": "Initial B5 symbolic mapping type errors repaired using explicit dict[str,Any]; approved static adapter then passed. Prior path/import/basis recovery preserved in earlier handoffs. No unresolved incident.",
    "presentation_policy": "evaluation-ancillary-v1",
    "rendering_performed": False,
}
write("supplementary/b5-final-audit.json", audit)
handoff = {
    "current_block": "B5",
    "completion_status": "complete",
    "next_block": "closure",
    "entry_exit_reason": "Exact symbolic identities, domain/sign/normalization and global telescoping proof complete; static checks, final clean-kernel execution and twelve-item source audit passed.",
    "operational_status": "completed",
    "run_status": "completed",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "unresolved_work": [],
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": True,
    "lyapunov_proof_verified": True,
    "evidence": [
        "state/pgm_b5.json",
        "supplementary/b5-final-audit.json",
        "supplementary/b5-final-execution.json",
        "supplementary/b5-static-002.json",
        "supplementary/pgm_example_lyap_checklist.md",
    ],
    "notebook": "pgm_example_lyap.ipynb",
    "notebook_sha256": digest,
    "finished_utc": now,
    "original_deadline_utc": "2026-09-23T23:46:30.668388+00:00",
    "access_control": "instruction_only",
    "prohibited_sources_observed": False,
}
write("supplementary/b5-handoff.json", handoff)
print(json.dumps(handoff, indent=2))
