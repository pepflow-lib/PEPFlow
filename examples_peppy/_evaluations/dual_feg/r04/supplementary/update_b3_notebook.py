"""Show B3 partial-sum construction and its current confirmation status."""

import hashlib
import os
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / "supplementary/.runtime"
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "MPLCONFIGDIR",
    "IPYTHONDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    p = runtime / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
path = ROOT / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
cells = [
    md(r"""## Partial-sum Lyapunov construction and rank profile
Use the saved numerical certificate, with $V_0=0$. For $k<N-1$, define
$$V_{k+1}-V_k=\lambda_k^{\rm Lip}\bigl(\|A(x_k)-A(x_{k+1/2})\|^2-L^2\|x_k-x_{k+1/2}\|^2\bigr)-\lambda_k^{\rm Mon}\langle A(x_{k+1/2})-A(x_N),x_{k+1/2}-x_N\rangle.$$
At the last step, retain only the Lipschitz term between $x_{N-1}$ and $x_N$. All multipliers are nonnegative, so these increments are nonpositive. The terminal-root monotonicity inequality and the whole PSD remainder $S$ are the two boundary contributions, one of each permitted type. The initial normalization remains part of the boundary argument.

The rank-one candidate differs from the numerical $S$ by $2.1\times10^{-5}$, so the construction retains the exact saved numerical matrix as one PSD boundary block. No contribution is omitted. At $N=6$, interior ranks are four with fixed exclusions $(1,1)$ and absolute rank tolerance $10^{-4}$, without rescaling. A second horizon remains required before B3 can be complete.
"""),
    code(
        "REPO_ROOT = repo_root\ncertificate = json.loads((notebook_dir / 'state/dual_feg_b2.json').read_text())\nN_int = certificate['N_verify']\nparams_sp = {'L': sp.S.One, 'R': sp.S.One}\nctx, pb, obj = get_pep_setup(N_int, params_sp)\npb.set_relaxed_constraints(certificate['relaxed_constraints'])"
    ),
    code((ROOT / "supplementary/b3_certificate_check.py").read_text()),
    code((ROOT / "supplementary/b3_decomposition.py").read_text()),
    code((ROOT / "supplementary/b3_grouping.py").read_text()),
]
for i, cell in enumerate(cells):
    cell.id = f"b3-{i:02d}"
    if cell.cell_type == "markdown":
        assert not any(c in cell.source for c in ("\x0c", "\r", "\x08"))
        assert "\\(" not in cell.source and "\\[" not in cell.source
nb.cells = [c for c in nb.cells if c.id != "b1-13" and not c.id.startswith("b3-")]
index = next(i for i, c in enumerate(nb.cells) if c.id == "b1-14")
nb.cells[index:index] = cells
nbformat.write(nb, path)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="dual-feg-owned",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nbformat.write(nb, path)
for cell in cells:
    for out in cell.get("outputs", []):
        if out.output_type == "stream":
            print(out.text)
checkpath = ROOT / "supplementary/dual_feg_example_lyap_checklist.md"
lines = checkpath.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B3 (incomplete: second horizon needed)"
    elif line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest()
    elif line.startswith("| 9."):
        lines[i] = (
            "| 9. partial-sum Lyapunov construction and rank profile | pending | b3-00 through b3-04 | N=6 certificate revalidation, rank and complete coverage passed; second-horizon confirmation pending. |"
        )
checkpath.write_text("\n".join(lines), encoding="utf-8")
print("B3 partial notebook executed; second-horizon confirmation pending.")
