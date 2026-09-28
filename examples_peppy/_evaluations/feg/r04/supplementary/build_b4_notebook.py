import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
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
nb.cells = nb.cells[:22]
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
nb.cells += [
    md(
        "## Identify the vectors composing the Lyapunov function\nStarting from the verified partial sums, search for interpretable vectors spanning their quadratic matrices. The retained interior is $1\\leq k\\leq N-1$; $k=0,N$ are both checked separately. Rank two was confirmed at horizons 4 and 6."
    ),
    code("""b3 = json.loads((notebook_dir / "state/feg_b3.json").read_text())
assert certificate["certificate_id"] == b3["certificate_id"]
assert ranks == b3["rank_profile"]
assert certificate_checked and grouping_checked
assert rank_evidence["summary"] == b3["rank_search"]
for k, Vk in enumerate(lyap):
    actual = pm.eval_scalar(Vk)
    assert np.allclose(actual.inner_prod_coords, b3["lyap_inner_prod_coords"][k], atol=1e-4, rtol=1e-5)
    assert np.allclose(actual.func_coords, b3["lyap_func_coords"][k], atol=1e-4, rtol=1e-5)
    assert np.allclose(actual.offset, b3["lyap_offsets"][k], atol=1e-4, rtol=1e-5)
print("Selected rank profile:", ranks, "interior: 1..N-1; exceptional indices: 0,N")
"""),
    md(
        "### Candidate-vector scan\nUse all full and half-step iterates, operator outputs, solution gaps, anchor gaps, and pairwise differences. Remove duplicate coordinate vectors and skip zero vectors, preferring meaningful labels. Then filter candidates to each quadratic column space."
    ),
]
for filename in ("b4_candidates.py", "b4_filter.py"):
    nb.cells.append(
        code((root / "supplementary" / filename).read_text(encoding="utf-8-sig"))
    )
nb.cells.append(
    md(
        "### Selected basis pattern\nThe sparse search is executed below for every nonzero index, including the terminal index. Its choices are compared with a uniform basis that follows the recurrence."
    )
)
nb.cells.append(
    code((root / "supplementary/b4_search.py").read_text(encoding="utf-8-sig"))
)
nb.cells.append(
    md(r"""The automatic search sometimes prefers differences involving the next half-step. For a common interpretation across the initial, interior and terminal cases, adopt
$$\mathcal B_k=[A(x_k),\ x_k-x_0],\qquad 1\leq k\leq N,$$
with the empty basis at $k=0$. The chosen basis is independently checked for full rank and reconstruction below; no future half-step is needed at $k=N$.
""")
)
nb.cells.append(
    code((root / "supplementary/b4_basis.py").read_text(encoding="utf-8-sig"))
)
nb.cells.append(
    md(
        "### Coefficient matrices\nThe basis order is operator output first, anchor gap second at every nonzero index. Off-diagonal entries contribute twice. The empty initial basis represents $V_0=0$; every function-value and constant coordinate is also checked."
    )
)
nb.cells.append(
    code((root / "supplementary/b4_coefficients.py").read_text(encoding="utf-8-sig"))
)
nb.cells.append(
    code(
        (root / "supplementary/b4_structure.py").read_text(encoding="utf-8-sig")
        + "\n"
        + (root / "supplementary/b4_reconstruction.py").read_text(encoding="utf-8-sig")
    )
)
nb.cells.append(
    md(r"""### Block 4 conclusion
The complete numerical structure is $V_0=0$ and, for $1\leq k\leq N$,
$$V_k=c_{00}(k,N,L)\|A(x_k)\|^2+2c_{01}(k,N,L)\langle A(x_k),x_k-x_0\rangle+c_{11}(k,N,L)\|x_k-x_0\|^2.$$
There are no function-value or constant terms. The three coefficient functions remain analytic unknowns; the displayed numerical matrices and reconstruction checks apply to the selected certificate. Block 5 must derive the coefficients from the recurrence and verify exact step, base and boundary identities before a theorem is claimed.

## Closed-form Lyapunov function and symbolic identities
Pending Block 5.
""")
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
    "Last reviewed block: B3", "Last reviewed block: B4"
)
text = re.sub(
    r"SHA-256: [a-f0-9]+",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    text,
)
text = text.replace(
    "| 10. special-vector identification | pending | Later-block obligation; placeholder only |",
    "| 10. special-vector identification | verified | 22-33: visible candidate construction/filtering and sparse search, common basis, all-index independence and reconstruction |",
)
text = text.replace(
    "| 11. coefficient extraction and closed-form V_k | pending | Later-block obligation; placeholder only |",
    "| 11. coefficient extraction and closed-form V_k | pending | 31-34: numerical matrices and full-component reconstruction verified at all indices; closed form deferred to B5 |",
)
checkpath.write_text(text)
print("B4 notebook executed; cells", len(nb.cells))
