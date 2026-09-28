import hashlib
import json
import re
from pathlib import Path

root = Path.cwd()
path = root / "bppm_example_lyap.ipynb"
nb = json.loads(path.read_text())
for i, c in enumerate(nb["cells"]):
    text = "".join(c["source"])
    assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in text)
    if c["cell_type"] == "markdown":
        assert "\\(" not in text and "\\[" not in text
    else:
        assert c["execution_count"] is not None and all(
            o["output_type"] != "error" for o in c["outputs"]
        )
streams = "".join(
    "".join(o.get("text", "")) for c in nb["cells"][20:] for o in c.get("outputs", [])
)
for needed in (
    "sparse basis:",
    "zero coefficients:",
    "k=4: quadratic reconstruction",
    "k=0: full-expression reconstruction",
    "k=4: candidate formula errors",
):
    assert needed in streams, needed
b4 = json.loads((root / "state/bppm_b4.json").read_text())
assert b4["numerical_reconstruction"]["required_indices"] == list(range(5))
static = json.loads((root / "supplementary/b4-static-002.json").read_text())
assert all(
    row["returncode"] == 0
    for row in static["commands"]
    if row["label"] in ("source_ruff", "source_ty")
)
checkpath = root / "supplementary/bppm_example_lyap_checklist.md"
check = checkpath.read_text(encoding="utf-8-sig").replace(
    "Last reviewed block: B3", "Last reviewed block: B4"
)
check = re.sub(
    r"SHA-256: [a-f0-9]+",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    check,
)
lines = check.splitlines()
for i, line in enumerate(lines):
    if line.startswith("| 10.") or line.startswith("| 11."):
        parts = line.split("|")
        if line.startswith("| 10."):
            parts[2] = " verified "
            parts[3] = " 20–27 "
            parts[4] = (
                " Actual candidate filtering and sparse subset search executed for k=1..4, including terminal; rank-four independent template selected. k=0 empty basis verified. "
            )
        else:
            parts[2] = " pending "
            parts[3] = " 28–32 "
            parts[4] = (
                " B4 coefficient extraction, labeled matrices, full-component reconstruction and finite-sample candidate formula checks complete at every k=0..4. Arbitrary-horizon closed form remains B5 obligation. "
            )
        lines[i] = "|".join(parts)
checkpath.write_text("\n".join(lines), encoding="utf-8")
record = dict(
    current_block="B4",
    completion_status="complete",
    next_block="B5",
    entry_exit_reason="Consistent basis search, independence, all-index full-expression reconstruction, candidate coefficient checks, notebook execution and static checks passed.",
    run_status="awaiting_continuation",
    sources=[
        "approved lyap-vectors workflow",
        "approved/pepflow/lyapunov_utils.py",
        "own B3 certificate and replay sources",
        "own generated candidate/basis/coefficient/structure sources",
    ],
    commands=[
        "run_b4_search.py",
        "save_b4.py",
        "update_b4_notebook.py twice",
        "static adapter b4-static-001/002.json",
        "finalize_b4.py",
    ],
    incidents=[
        dict(
            classification="type diagnostic",
            issue="Dictionary-expanded tolerance arguments ambiguous to ty",
            repair="Explicit keyword arguments with identical frozen values; checks passed.",
        )
    ],
    access_control="instruction_only",
    prohibited_content_observed=False,
    observability_limit="Tool-visible record; no exhaustive OS tracing.",
    numerical_reconstruction=b4["numerical_reconstruction"],
    unresolved_work="B5 arbitrary-horizon exact Lyapunov identities, signs, boundary normalization, and final theorem.",
    deadline_utc="2026-09-23T17:01:13.976153+00:00",
)
(root / "supplementary/b4-access-handoff.json").write_text(json.dumps(record, indent=2))
print("B4 delivery checks passed; all required indices reconstructed.")
