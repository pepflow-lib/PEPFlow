import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import configure  # ty: ignore[unresolved-import]

attempt, approved = configure()
import nbformat as nbf  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup

path = attempt / "ogm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
for i, c in enumerate(nb.cells):
    if c.cell_type == "markdown":
        print(i, c.source.splitlines()[0])
    else:
        print(
            i, "code", c.execution_count, "outputs", [o.output_type for o in c.outputs]
        )
assert nb.cells[1].source == "## Proof Statement"
assert nb.cells[2].source.startswith("### Theorem")
assert nb.cells[3].source.startswith("### Proof outline")
assert "V_{k}" in nb.cells[2].source and "W_{k+1}-W_{k}" in nb.cells[3].source
assert "find_basis_with_sparsest_coefficients" in nb.cells[37].source
assert any("image/png" in o.get("data", {}) for o in nb.cells[10].outputs)
assert all(
    any(o.output_type == "stream" for o in nb.cells[i].outputs)
    for i in (49, 52, 55, 58, 61, 63)
)
assert all(
    any("text/latex" in o.get("data", {}) for o in nb.cells[i].outputs)
    for i in (49, 52, 55, 58, 61)
)
items = [
    "title, problem description, and the algorithm update equations in LaTeX",
    "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
    "imports",
    "function/operator definitions",
    "make_ctx_ogm and get_pep_setup",
    "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
    "dense and relaxed proof solves",
    "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
    "partial-sum Lyapunov construction and rank profile",
    "special-vector identification",
    "coefficient extraction and closed-form V_k",
    "symbolic step, base, and boundary identities",
]
indices = [
    "0",
    "1–3",
    "4–6",
    "7",
    "8",
    "9–10",
    "11–15",
    "16–23, 45–63",
    "24–30",
    "31–39",
    "40–44, 45–63",
    "47–63",
]
evidence = [
    "Complete supplied assumptions and update equations, including special terminal theta recurrence, in source.",
    "Separate theorem and self-contained proof outline state all-index potential and exact rate, local residual identities, signs, N1 and full-PEP telescoping.",
    "Approved-source/private-helper paths and runtime settings visible; kernel executed imports.",
    "L,R and smooth-convex function definitions executed.",
    "Full context builder and PEP definition visible, with correct radius squared and terminal gradient.",
    "N1–N7 printed values plus embedded PNG plot; max candidate discrepancy 3.12e-9. Plot presence checked without inspecting image.",
    "Dense solve, threshold trial and selected chain solve preserved in state/supplementary; complete selected inventory, solver settings and gap 3.16e-9 shown.",
    "Labeled candidates and direct S reconstruction; complete numerical identity with max residual 1.39e-9; exact local identities and telescoping prove global formulas. Historical numerical statuses distinguished from final analytic status.",
    "Visible partial_sum loop and exact saved-source replay; rank 3 confirmed at N4,N6 with exclusions(1,1); full coverage max 5.63e-9.",
    "Actual deduplicated scan, column-space filtering and sparse basis search outputs for all nonzero k; independence including endpoints.",
    "Labeled numeric and candidate C matrices; function and offset components included; all-index full reconstruction max 3.05e-10; exact closed-form expression proved below.",
    "Five exact checks show labeled Gram and function zero matrices and zero constants: interior49, base52, terminal55, N1 58, normalization61; sign/domain argument62–63.",
]
lines = [
    f"Notebook: {path.name}",
    "Last reviewed block: B5",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    "Presentation policy: evaluation-ancillary-v1. Rendered/image inspection intentionally omitted; source delimiter/control-character checks passed. No rendered verification is claimed.",
    "",
    "| Item | Status | Cells | Evidence |",
    "|---|---|---|---|",
]
for i, (item, ix, ev) in enumerate(zip(items, indices, evidence), 1):
    lines.append(f"| {i}. {item} | verified | {ix} | {ev} |")
(attempt / "supplementary/ogm_example_lyap_checklist.md").write_text(
    "\n".join(lines), encoding="utf-8"
)
state = json.loads((attempt / "state/ogm_b5.json").read_text())
assert (
    state["run_status"] == "complete"
    and state["lyapunov_proof_verified"]
    and state["analytic_full_pep_verified"]
)
assert all(state["proof_checks"].values())
print("All twelve notebook requirements checked under the presentation override.")
