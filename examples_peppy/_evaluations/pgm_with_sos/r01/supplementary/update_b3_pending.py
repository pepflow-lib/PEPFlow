import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import json
import os

# optional notebook-generation dependency
import nbformat as nb  # ty: ignore[unresolved-import]
import runtime

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
path = root / "pgm_example_lyap.ipynb"
book = nb.read(path, as_version=4)
intro = nb.v4.new_markdown_cell(r"""## Lyapunov partial sums and ranks
For normalized interpolation residuals $I_q\le0$, define $V_0=0$ and
$$V_k=\sum_{q\text{ assigned through }k}\lambda_q I_q-\sum_{i=1}^{k}\sum_{r=1}^{3}c_{r,i}\|u_{r,i}\|^2.$$
The initial $f$ residual from $x_\star$ to $x_0$ is included in the first increment. At step $k$ add the optimum-to-$x_k$ and predecessor-to-$x_k$ residuals for both functions, then subtract the three supplied squares at $k$. Thus each increment is nonpositive. All interpolation terms and all squares are covered; the radius constraint remains for the final boundary argument.

The first observation at $N=4$ has interior rank 4 after excluding $V_0,V_N$, with absolute rank tolerance $10^{-4}$ on unscaled Gram coordinates. A second horizon is required before B3 can be completed. An $N=6$ certificate acquisition is pending in B2.""")
code = (
    """basis = ctx_b2.basis_vectors()
S_scalar = sum((float(S_saved[i,j])*basis[i]*basis[j]
                for i,j in np.ndindex(S_saved.shape)),pf.Scalar.zero())
saved_identity = pm.eval_scalar(pb_b2.performance_metric-b2["opt_value"]-weighted+S_scalar)
assert all(maxabs(v)<=1e-5 for v in (saved_identity.inner_prod_coords,saved_identity.func_coords,saved_identity.offset))
"""
    + (root / "supplementary/b3_decomposition.py").read_text()
    + "\n"
    + (root / "supplementary/b3_grouping.py").read_text()
)
book.cells = book.cells[:13] + [intro, nb.v4.new_code_cell(code)] + book.cells[-2:]
nb.write(book, path)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(
    book,
    timeout=180,
    kernel_name="pgm-attempt",
    resources={"metadata": {"path": str(root)}},
).execute()
nb.write(book, path)
# Preserve the coherent selected sample before the requested B2 revisit.
(root / "supplementary/certificate_N4.json").write_text(
    (root / "state/pgm_b2.json").read_text()
)
rank = json.loads((root / "supplementary/rank_N4.json").read_text())
rank["certificate_path"] = "supplementary/certificate_N4.json"
(root / "supplementary/rank_N4.json").write_text(json.dumps(rank, indent=2))
record = dict(
    current_block="B3",
    completion_status="incomplete",
    next_block="B2",
    requested_N=6,
    entry_exit_reason="Promising N4 rank and complete coverage; second-horizon coherent certificate required",
    operational_status="awaiting_same_session_continuation",
    sources=[
        "supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md",
        "state/pgm_b2.json",
        "pgm_example_lyap.ipynb",
        "supplementary/b3_certificate_check.py",
        "supplementary/b3_decomposition.py",
        "supplementary/b3_grouping.py",
    ],
    commands=[
        "Pinned Python -I -B supplementary/run_b3.py",
        "Pinned Python -I -B supplementary/update_b3_pending.py",
    ],
    access_control="instruction_only",
    prohibited_sources_observed=False,
    audit_limit="No exhaustive filesystem read audit",
    evidence="supplementary/rank_N4.json",
    unresolved_work="Cross-horizon rank confirmation; B4-B5",
    deadline_utc="2026-09-23T16:12:00.406449+00:00",
)
(root / "supplementary/b3-handoff-001.json").write_text(json.dumps(record, indent=2))
check = root / "supplementary/pgm_example_lyap_checklist.md"
t = check.read_text().replace(
    "Last reviewed block: B2",
    "Last reviewed block: B3 (incomplete; B2 revisit required)",
)
import re  # noqa: E402 - imports follow runtime or notebook setup

t = re.sub(
    r"SHA-256: [a-f0-9]+",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    t,
)
t = t.replace(
    "| pending | 13 | Due B3. |",
    "| pending | 13,14 | N4 rank and complete coverage executed; second-horizon confirmation still required. |",
)
t = (
    t.replace("| pending | 14 | Due B4. |", "| pending | 15 | Due B4. |")
    .replace("| pending | 15 | Due B4/B5. |", "| pending | 16 | Due B4/B5. |")
    .replace("| pending | 15 | Due B5. |", "| pending | 16 | Due B5. |")
)
check.write_text(t)
print("Pending B3 notebook executed; N4 preserved; awaiting B2 N6 certificate.")
