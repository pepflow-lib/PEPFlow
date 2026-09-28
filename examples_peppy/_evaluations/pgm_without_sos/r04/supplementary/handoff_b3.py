import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import json

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import runtime

root = runtime.ATTEMPT
nb_path = root / "pgm_example_lyap.ipynb"
nb = nbf.read(nb_path, as_version=4)
i = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum")
)
nb.cells[i].source = r"""## Partial-sum Lyapunov construction and ranks
Block 3 is in progress. At $N=4$, the complete saved certificate revalidates. The initial reverse-LDL assignment gives ranks $[0,4,4,4,1]$ at absolute tolerance $10^{-4}$. All interpolation terms and all LDL pieces are included; full-coordinate coverage and increment residuals are below $1.2\times10^{-16}$. The fixed proposed boundary exclusion is one index at each end.
A second horizon is required before rank confirmation. The complete current observation, singular values and partial sums are preserved in `supplementary/sample_n4/`. Block 2 must now obtain a coherent certificate at $N=6$; no Block 3 completion or analytic claim is made yet."""
nbf.write(nb, nb_path)
checklist = root / "supplementary/pgm_example_lyap_checklist.md"
text = checklist.read_text(encoding="utf-8-sig")
text = text.replace("Last reviewed block: B2", "Last reviewed block: B3 (in progress)")
import re  # noqa: E402 - imports follow runtime or notebook setup

text = re.sub(
    r"SHA-256: [A-Fa-f0-9]+",
    "SHA-256: " + hashlib.sha256(nb_path.read_bytes()).hexdigest(),
    text,
)
text = text.replace(
    "| pending | 18 | Due B3. |",
    "| pending | 18 | N=4 observation and full-coordinate checks preserved; second-horizon confirmation and final visible construction still required. |",
)
checklist.write_text(text)
record = dict(
    current_block="B3",
    completion_status="incomplete",
    next_block="B2",
    requested_horizon=6,
    entry_exit_reason="Additional coherent certificate required for cross-horizon rank confirmation",
    operational_status="awaiting_same_session_continuation",
    deadline_utc="2026-09-23T21:58:02.889281+00:00",
    sources_added=[
        "approved lyap-define/references/workflow.md",
        "own B2 certificate and generated B3 sources/artifacts",
    ],
    commands=[
        "scoped Get-Content",
        "pinned python -I -B explore_b3.py",
        "pinned python -I -B observe_b3.py",
        "pinned python -I -B handoff_b3.py",
    ],
    observations="supplementary/sample_n4/observation.json",
    access_control="instruction_only",
    prohibited_content_observed=False,
    audit_limit="No exhaustive OS read tracing",
    unresolved_work="Cross-horizon rank comparison, complete B3 notebook construction, B4 and B5",
)
(root / "supplementary/b3-revisit-handoff.json").write_text(
    json.dumps(record, indent=2)
)
