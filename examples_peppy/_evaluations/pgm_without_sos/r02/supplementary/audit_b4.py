# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import contextlib
import hashlib
import json

import numpy as np

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
from pgm_setup import (  # noqa: F401 -- Required by exec of pgm_b4.json#certificate_check_code.
    get_pep_setup,
)

# Preserve the recorded import initialization order.
# isort: split
from pgm_setup import (  # noqa: F401 -- Required by exec of pgm_b4.json#certificate_check_code.
    f,
    g,
)

notebook_dir = runtime.ROOT
b4 = json.loads((notebook_dir / "state/pgm_b4.json").read_text())
certificate = b4
with (
    (notebook_dir / "supplementary/b4-replay.log").open("w") as log,
    contextlib.redirect_stdout(log),
):
    for field in [
        "certificate_check_code",
        "decomposition_code",
        "grouping_code",
        "basis_code",
    ]:
        exec(compile(b4[field], field, "exec"))
    coeff_by_k = {
        int(k): np.array(v, dtype=float).reshape((len(V_k_basis(int(k))),) * 2)
        for k, v in b4["coeff_by_k"].items()
    }
    exec(compile(b4["structure_code"], "structure_code", "exec"))
    for k in range(N + 1):
        value = pm.eval_scalar(V_k_structure(k) - lyap[k])
        assert (
            max(
                max_abs(value.inner_prod_coords),
                max_abs(value.func_coords),
                max_abs(value.offset),
            )
            < 1e-4
        )
nb_path = notebook_dir / "pgm_example_lyap.ipynb"
nb = json.loads(nb_path.read_text())
for cell in nb["cells"]:
    code = "".join(cell["source"])
    if cell["cell_type"] == "markdown":
        assert code.count("$") % 2 == 0 and not any(
            x in code for x in ["\\(", "\\)", "\\[", "\\]", "\x0c", "\r"]
        )
    else:
        assert cell["execution_count"] is not None
        assert all(o["output_type"] != "error" for o in cell["outputs"])
assert (
    len([o for o in nb["cells"][49]["outputs"] if "text/latex" in o.get("data", {})])
    == 5
)
p = notebook_dir / "supplementary/pgm_example_lyap_checklist.md"
lines = p.read_text(encoding="utf-8-sig").splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B4"
    elif line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(nb_path.read_bytes()).hexdigest()
    elif line.startswith("| 10 |"):
        lines[i] = (
            "| 10 | special-vector identification | verified | 38-47 | Actual 505-candidate scan, sparse-basis search at k=1..4, uniform rank-4 interior basis and endpoint independence checked. |"
        )
    elif line.startswith("| 11 |"):
        lines[i] = (
            "| 11 | coefficient extraction and closed-form V_k | pending | 48-52 | B4 numerical matrices and full-component reconstructions verified for 0..4; saved-source replay passed. Closed-form coefficients remain B5 work. |"
        )
    elif line.startswith("| 12 |"):
        lines[i] = (
            "| 12 | symbolic step, base, and boundary identities | pending | 53 | B5. |"
        )
p.write_text("\n".join(lines) + "\n")
record = dict(
    current_block="B4",
    completion_status="complete",
    next_block="B5",
    entry_exit_reason="Every-index basis and full-expression reconstruction verified",
    operational_status="awaiting_same_session_continuation",
    access_control="instruction_only",
    consulted_sources=[
        "Approved lyap-vectors/references/workflow.md",
        "Own B3/B4 sources, state, evidence and notebook",
    ],
    prohibited_content_observed=False,
    evidence=[
        "supplementary/b4-verification.log",
        "supplementary/b4-replay.log",
        "supplementary/b4-static-001.json",
    ],
    remaining="Analytic coefficient derivation and exact step/base/boundary proof",
    audit_limit="No exhaustive filesystem tracing",
)
(notebook_dir / "supplementary/b4-access-record.json").write_text(
    json.dumps(record, indent=2)
)
print("B4 saved-source replay and notebook content audit passed.")
