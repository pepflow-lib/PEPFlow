import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import json
import re

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
from jupyter_client import KernelManager

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
path = root / "feg_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
nb.cells = nb.cells[:17]
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
b3 = json.loads((root / "state/feg_b3.json").read_text())
nb.cells.append(
    md(r"""## Partial-sum Lyapunov construction
Write $r^{\rm Lip}_j=\|A(x_j)-A(x_{j-1/2})\|^2-L^2\|x_j-x_{j-1/2}\|^2\leq0$ and $r^{\rm mon}_k=-\langle A(x_{k+1})-A(x_k),x_{k+1}-x_k\rangle\leq0$. Using the selected numerical multipliers, set $V_0=0$ and
$$V_{k+1}-V_k=\lambda^{\rm Lip}_{k+1}r^{\rm Lip}_{k+1}+\mathbf{1}_{k\geq1}\lambda^{\rm mon}_{k}r^{\rm mon}_{k}.$$
The multipliers are nonnegative, so this convention gives $V_{k+1}\leq V_k$. Keep the single final zero-point monotonicity residual and the entire positive-semidefinite $S$ block for the boundary argument. No interpolation or square term is omitted.

The same recipe gives interior rank two at $N=4$ and $N=6$, excluding only $V_0,V_N$. The rank uses absolute singular values with threshold $10^{-4}$ in the setup's coordinate order. Coverage is checked in Gram, function-value and constant coordinates. This remains finite-sample structure discovery, not an arbitrary-horizon proof.
""")
)
check_source = (
    b3["certificate_check_code"]
    .replace("from certificate import digest, inventory, verify\n", "")
    .replace("from feg_setup import get_pep_setup\n", "")
)
check_source = check_source.replace(
    "N_int = certificate",
    'certificate = json.loads((notebook_dir / "state/feg_b2.json").read_text())\nN_int = certificate',
    1,
)
nb.cells.append(code(check_source.split("\n", 1)[1]))
nb.cells.append(code(b3["decomposition_code"]))
nb.cells.append(code(b3["grouping_code"]))
nb.cells.append(
    code("""rank_evidence = json.loads((notebook_dir / "supplementary/rank_search.json").read_text())
samples = rank_evidence["samples"]
assert len({s["N"] for s in samples}) >= 2
assert len({s["recipe_id"] for s in samples}) == 1
assert all(s["rank_convention"] == samples[0]["rank_convention"] for s in samples)
assert all(s["certificate_checked"] and s["grouping_checked"] and s["rank_credible"] for s in samples)
retained_profiles = [s["rank_profile"][1:s["N"]] for s in samples]
assert all(len(r) >= 3 and len(set(r)) == 1 for r in retained_profiles)
assert len({r[0] for r in retained_profiles}) == 1
# Each complete sample was independently reconstructed by the exact code above
# during finalize_b3.py; its certificate, source, coverage and singular values
# are retained in supplementary/ rather than mixed into the selected sample.
for sample in samples:
    print("N:", sample["N"], "retained ranks:", sample["rank_profile"][1:sample["N"]], "coverage:", sample["coverage_residuals"])
print("Common interior rank:", retained_profiles[0][0], "exclusions:", (1, 1))
print("Selected full profile:", ranks, "final rank:", ranks[-1])
print("Boundary interpolation count:", len(boundary_names), "boundary S blocks:", len(boundary_S))
""")
)
nb.cells.append(
    md(
        "## Identify the vectors composing the Lyapunov function\nPending Block 4.\n\n## Closed-form Lyapunov function and symbolic identities\nPending Block 5."
    )
)
nbf.write(nb, path)
km = KernelManager(kernel_name="feg-private")
km.kernel_spec_manager.kernel_dirs = [str(runtime.RUNTIME / "jupyter/kernels")]
try:
    NotebookClient(
        nb, km=km, timeout=180, resources={"metadata": {"path": str(root)}}
    ).execute()
finally:
    if km.has_kernel:
        km.shutdown_kernel(now=True)
nbf.write(nb, path)
for c in nb.cells:
    if c.cell_type == "markdown":
        assert "\\(" not in c.source and "\\[" not in c.source
        assert not any(ch in c.source for ch in ("\r", "\x0c", "\x08"))
assert not any(
    o.output_type == "error"
    for c in nb.cells
    if c.cell_type == "code"
    for o in c.outputs
)
checkpath = root / "supplementary/feg_example_lyap_checklist.md"
text = checkpath.read_text().replace(
    "Last reviewed block: B2", "Last reviewed block: B3"
)
text = re.sub(
    r"SHA-256: [a-f0-9]+",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    text,
)
text = text.replace(
    "| 9. partial-sum Lyapunov construction and rank profile | pending | Later-block obligation; placeholder only |",
    "| 9. partial-sum Lyapunov construction and rank profile | verified | 17-21: complete reconstruction, visible S ingredients and grouping, line-by-line ranks, coverage and two-horizon summary; no rendering under evaluation policy |",
)
checkpath.write_text(text)
print("B3 notebook executed; cells", len(nb.cells))
