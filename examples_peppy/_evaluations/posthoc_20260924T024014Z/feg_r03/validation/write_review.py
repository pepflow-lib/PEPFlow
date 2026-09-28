import datetime
import hashlib
import json
from pathlib import Path

import numpy as np

v = Path(chr(92) * 2 + "?" + chr(92) + str(Path(__file__).resolve().parent))
r = v.parent
orig = r.parent.parent / "feg/r03"


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def write(name, data):
    (r / name).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


hashes = read(r / "submission-hashes.json")
checksums = []
for name, expected in hashes.items():
    p = orig / name
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    checksums.append(
        dict(path=str(p), expected=expected, actual=actual, match=actual == expected)
    )
write(
    "original-hash-verification.json",
    dict(
        checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        count=len(checksums),
        all_match=all(x["match"] for x in checksums),
        files=checksums,
    ),
)
assert all(x["match"] for x in checksums)
assert (
    hashlib.sha256((v / "feg_example_lyap.ipynb").read_bytes()).hexdigest()
    == hashes["feg_example_lyap.ipynb"]
)
b1 = read(v / "state/feg_b1.json")
b2 = read(v / "state/feg_b2.json")
b4 = read(v / "state/feg_b4.json")
dense = read(v / "state/feg_dense.json")
replay = read(v / "replay-results.json")
S = np.asarray(b2["S_matrix"])
D = np.asarray(b2["numerical_decomposition"]["D"])
E = np.asarray(b2["numerical_decomposition"]["ell_coords"])
num = dict(
    certificate_id=b2["certificate_id"],
    dense_relaxed_gap=abs(dense["opt_value"] - b2["opt_value"]),
    min_dual=min(float(x) for x in b2["named_dual_values"].values() if x is not None),
    min_S_eigenvalue=float(np.linalg.eigvalsh(S).min()),
    S_reconstruction_max=float(np.max(np.abs(E.T @ D @ E - S))),
    identity_residuals=replay["residuals"],
    tolerances=b2["numerical_checks"],
)
write("numerical-evidence.json", num)
write(
    "operational-incidents.json",
    [
        dict(
            stage="historical",
            incident="Pinned python -m jupyter selected Python313 jupyter-nbconvert launcher; symbolic matrix display then raised TypeError: Cannot convert expression to float.",
            evidence_ref="validation/supplementary/b5-final-execution.json",
            resolution="Fresh pinned isolated Python replay; no launcher dispatch; display calls omitted in validation only.",
        ),
        dict(
            stage="posthoc inspection",
            incident="PowerShell and first Python inspection could not read long generic skill paths (FileNotFoundError).",
            before="Path(__file__).resolve().parent",
            after="Windows extended path prefix \\\\?\\ on owned review path",
            resolution="All own skill files readable with extended paths; no mathematical change.",
        ),
        dict(
            stage="posthoc N6 replay",
            incident="NameError: name 'REPO_ROOT' is not defined at b3_certificate_check.py line 39",
            evidence_ref="validation/rank6-output-failed-001.txt",
            before="REPO_ROOT absent from standalone replay namespace",
            after="REPO_ROOT=root/'supplementary/approved'",
            resolution="Added required validation-local generic framework path; N6 certificate/grouping replay passed.",
        ),
    ],
)
nbref = "validation/feg_example_lyap.ipynb"
checks = []


def add(name, result, ref, status="PASS"):
    checks.append(
        dict(name=name, status=status, observed_result=result, evidence_ref=ref)
    )


add(
    "Claim, algorithm and scope",
    "Prescribed monotone L-Lipschitz FEG updates, root condition and squared last-iterate residual. Shared x_(1/2)=x_0 explicitly checked. N>=1, L>0, R>=0; no stronger structural assumptions.",
    nbref + "#c987c862",
)
add(
    "Fully defined potential and coefficients",
    "V_0=0; V_k=2 k^2 ||g_k||^2/N^2+4 k L <g_k,x_k-x_0>/N^2 for 1<=k<=N. No function-value or constant terms. Explicit formula sufficient; submitted coefficient recurrence inspected without re-solving.",
    nbref + "#01261db3",
)
add(
    "General symbolic step",
    "Actual updates substituted with symbolic k,N,L; V_(k+1)-V_k - 2(k+1)^2 I_Lip/N^2 - 4Lk(k+1) I_Mon/N^2 has exactly zero Gram, function and constant components. Fresh submitted-cell replay.",
    "validation/replay-output.txt",
)
add(
    "Signs and domains",
    "I_Lip<=0 by L-Lipschitzness; I_Mon<=0 by monotonicity. Coefficients 2(k+1)^2/N^2, 4Lk(k+1)/N^2 positive on 1<=k<N. N,k+1,L nonzero. Final zero-point monotonicity residual and initial residual nonpositive; terminal square nonnegative.",
    nbref + "#94fe623d",
)
add(
    "Initial link",
    "Fresh exact V_1-V_0=(2/N^2)(||g_1-g_0||^2-L^2||x_1-x_0||^2), using x_1=x_0-g_0/L. All scalar components exactly zero; V_0=0.",
    "validation/replay-results.json",
)
add(
    "Terminal link and normalization",
    "Fresh exact metric-4L^2R^2/N^2=V_N+(4L/N)I_star-S_N+(4L^2/N^2)r_0. Therefore metric-target<=V_N<=V_0=0. Restores general L,R directly, not by unverified scaling.",
    "validation/replay-output.txt",
)
add(
    "Small horizons and degenerate radius",
    "N=1 uses empty interior range, same base and terminal identities; no division by R, so R=0 included.",
    nbref + "#94fe623d",
)
add(
    "B1 saved sweep",
    "Seven recorded CLARABEL optimal solves, N=1..7. Values retained in B1 state; N>=2 maximum discrepancy from 4/N^2 is 8.768811288195622e-9. N=1 approximately 2 versus target 4. Sweep inspected, not solved again.",
    "validation/state/feg_b1.json",
)
add("B2 coherent numerical certificate", num, "numerical-evidence.json")
add(
    "B3 partial sums, coverage, increments and rank",
    "Fresh saved-certificate replay at N=4 and N=6; all scalar-component coverage/increment checks pass. Rank 2 on k=1..N-1 with exclusions left=right=1, retaining 3 and 5 indices. Absolute rank tolerance 1e-4, no scaling. Explicit terminal zero-point monotonicity and full PSD remainder retained.",
    "validation/rank6-results.json",
)
add(
    "B4 bases and full reconstruction",
    "Fresh independence ranks [0,2,2,2,2]; saved symmetric coefficient matrices reconstruct all k=0..4. Maximum Frobenius residual 9.281881235489407e-9; maximum component Gram residual 6.358104487347305e-9; function and offset residuals zero. Search source and historical search output inspected, not rerun.",
    "validation/replay-results.json",
)
add(
    "Original static checks",
    "Latest b5-static-003: source_ruff=0, source_ty=0; expected missing-module negative probe=1. Earlier failures preserved.",
    "validation/supplementary/b5-static-003.json",
)
add(
    "Original final execution and checklist",
    "Original final notebook execution returncode 1 due to symbolic display; final checklist pending. Delivery remains incomplete.",
    "validation/supplementary/closure.json",
    "FAIL",
)
add(
    "Fresh validation execution",
    "28 selected code cells passed in fresh isolated pinned Python process; 3 discovery cells inspected and omitted; coefficient extraction replaced by saved coefficient loading; N6 saved certificate and grouping additionally replayed. This is validation-cell replay, not a full nbconvert rerun.",
    "validation/replay-results.json",
)
add(
    "Original preservation",
    str(len(checksums))
    + " original SHA256 hashes match; validation notebook also matches original hash.",
    "original-hash-verification.json",
)
blocks = []
for bid, reason, refs in [
    (
        "B1",
        "Algorithm/setup and saved seven-horizon sweep agree with supplied problem; rate comparison recorded.",
        ["validation/state/feg_b1.json", "validation/replay-output.txt"],
    ),
    (
        "B2",
        "Coherent saved certificate freshly replayed with frozen tolerances; dual signs, PSD, identity, S reconstruction, dense agreement pass. Initial formula-search record inspected.",
        ["numerical-evidence.json", "validation/replay-output.txt"],
    ),
    (
        "B3",
        "Two saved horizons freshly replayed under same grouping recipe; full coverage/increments and rank rule pass.",
        ["validation/rank6-results.json", "validation/replay-results.json"],
    ),
    (
        "B4",
        "Saved bases and coefficients freshly reconstruct all required indices and scalar components; historical search evidence retained.",
        [
            "validation/replay-results.json",
            "validation/supplementary/b4-complete-output.txt",
        ],
    ),
    (
        "B5",
        "Submitted exact local Lyapunov proof establishes target; fresh general step/base/terminal replay and sign/domain inspection pass. Original final notebook/checklist delivery failed operationally.",
        [
            "validation/replay-results.json",
            nbref + "#94fe623d",
            "validation/supplementary/closure.json",
        ],
    ),
]:
    blocks.append(
        dict(
            block_id=bid,
            mathematical_status="PASS",
            delivery_status="FAIL" if bid == "B5" else "PASS",
            reason=reason,
            evidence_refs=refs,
        )
    )
review = dict(
    attempt_id="feg_r03",
    mathematical_verdict="PASS",
    mathematical_reason="The submitted explicit Lyapunov function has a verified general nonpositive increment, exact shared-first-step identity and exact terminal square completion. The sign/domain argument yields ||A(x_N)||^2<=4 L^2 R^2/N^2 for every N>=1, including R=0. No mathematical expression or missing argument was repaired.",
    submitted_theorem="For prescribed FEG, monotone L-Lipschitz A with A(x_star)=0, L>0 and ||x_0-x_star||^2<=R^2, R>=0, every integer N>=1 satisfies ||A(x_N)||^2<=4 L^2 R^2/N^2.",
    target_scope_comparison="Exact target, assumptions, algorithm, metric, normalization, and full horizon range match.",
    verification_method={
        "replayed": "Submitted non-discovery notebook cells in fresh pinned python -I -B process; numerical certificate, saved basis reconstruction, exact symbolic general step/base/terminal; additional saved N6 certificate/grouping.",
        "inspected": "Own input/rubric/history, submitted generic skills and tolerance guidance, frozen notebook theorem and signs, coefficient derivation, historical sweep/search/static/access/delivery evidence. No external mathematics, other attempt, new solve/search or proof repair.",
    },
    mathematical_evidence_refs=[
        nbref + "#94fe623d",
        "validation/replay-output.txt",
        "validation/replay-results.json",
        "validation/rank6-results.json",
        "numerical-evidence.json",
    ],
    checks=checks,
    blocks=blocks,
    original_delivery_status="incomplete",
    original_delivery_reason="Original B5 final execution failed with symbolic-to-float display error after alternate generic nbconvert launcher; checklist pending and original closure completed only B1-B4. Historical records preserved.",
    posthoc_validation_execution_status={
        "status": "PASS",
        "scope": "Fresh selected-cell and saved-certificate replay, not full notebook discovery or nbconvert execution.",
        "executed_cells": 28,
        "omitted_discovery_cells": 3,
        "N6_saved_certificate_replayed": True,
        "evidence_refs": [
            "validation/replay-results.json",
            "validation/rank6-results.json",
        ],
    },
    access_findings={
        "generic_operational_incidents": [
            "Historical Python313 launcher/dependency consumption",
            "Historical symbolic matrix display failure",
            "Posthoc long-path inspection failure and missing standalone REPO_ROOT recovery",
        ],
        "prohibited_mathematical_exposure": {
            "status": "not_established",
            "evidence": [
                "own-generation-host-access-calls.json",
                "validation/supplementary/b5-access-incident.json",
                "validation/supplementary/b5-final-execution.json",
            ],
            "reason": "Inspected own host-call/access records show a concrete generic launcher incident, not target mathematical content. No prohibited mathematical exposure established by inspected evidence.",
        },
        "independence_eligible": True,
        "limitations": [
            "Instruction-only isolation and saved host calls are not exhaustive OS read tracing; absence of observed exposure does not prove absence of exposure."
        ],
        "decision_basis": "Explicit user override makes generic dependency-path/launcher/display problems operational; historical exclusion is not adopted as a mathematical finding.",
    },
    execution_adjustments=[
        "validation/execution-adjustments.json",
        "operational-incidents.json",
    ],
    review_started_at="2026-09-24T02:41:31.334160+00:00",
    review_stopped_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    limitations=[
        "No solver sweep, parameter search or basis discovery rerun; saved evidence inspected and certificates replayed.",
        "No complete nbconvert clean-kernel notebook rerun because discovery cells were intentionally excluded; fresh isolated selected-cell replay is separately reported.",
        "Original delivery remains incomplete; posthoc success does not backfill original block completion.",
        "No rendering required or performed.",
        "No claim of an independent all-horizon tightness proof.",
    ],
    historical_verdict_change={
        "from": "NOT_EVALUATED",
        "to": "PASS",
        "reason": "Explicit generic-operational override permits completing mathematical verification; newly replayed identities establish exact target.",
    },
)
write("review.json", review)
print(
    "review.json PASS; original hashes:",
    len(checksums),
    "all match; selected cells",
    len([x for x in replay["cells"] if x["status"] == "PASS"]),
)
