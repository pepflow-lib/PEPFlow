import hashlib
import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime", root / "supplementary/helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat as nbf  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
from jupyter_client import (  # noqa: E402 - imports follow runtime or notebook setup
    KernelManager,
)
from jupyter_client.kernelspec import (  # noqa: E402 - imports follow runtime or notebook setup
    KernelSpecManager,
)
from nbclient import (  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
    NotebookClient,
)

path = root / "dual_feg_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
intro = r"""## Partial-sum Lyapunov construction and rank profile
Use the selected coherent $N=6$ certificate, and define $V_0=0$. With $r_{\rm Lip}(u,v)=\|A(u)-A(v)\|^2-L^2\|u-v\|^2\le0$ and $r_{\rm Mon}(u,v)=-\langle A(u)-A(v),u-v\rangle\le0$, the construction is
$$V_{k+1}-V_k=\lambda_{\rm Lip,k}r_{\rm Lip}(x_k,y_k)+\lambda_{\rm Mon,k}r_{\rm Mon}(x_N,y_k),\quad 0\le k<N-1,$$
$$V_N-V_{N-1}=\lambda_{\rm Lip,N-1}r_{\rm Lip}(x_{N-1},x_N).$$
Nonnegative multipliers make this sequence nonincreasing. Terminal monotonicity $(x_N,x_\star)$ and the whole positive-semidefinite $S$ are the two boundary contributions. No weighted terms are omitted. The numerical rank is 4 on $1\le k\le N-1$ at both $N=4$ and $N=6$, using absolute singular-value tolerance $10^{-4}$ without scaling. Boundary ranks remain part of the subsequent proof obligations."""
init = """certificate = json.loads((notebook_dir / "state/dual_feg_b2.json").read_text())
REPO_ROOT = repo_root
N_int = certificate["N_verify"]
N = sp.Integer(N_int)
params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.Integer(1), "R": sp.Integer(1)}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
ctx.set_as_current()
"""
cells = [nbf.v4.new_markdown_cell(intro), nbf.v4.new_code_cell(init)]
for filename in ["b3_certificate_check.py", "b3_decomposition.py", "b3_grouping.py"]:
    cells.append(
        nbf.v4.new_code_cell(
            (root / "supplementary" / filename).read_text(encoding="utf-8-sig")
        )
    )
cells.append(
    nbf.v4.new_code_cell("""rank_evidence = json.loads((notebook_dir / "supplementary/rank_search.json").read_text())
for sample in rank_evidence["samples"]:
    kept = sample["rank_profile"][1:-1]
    assert len(kept) >= 3 and set(kept) == {4}
    assert sample["certificate_checked"] and sample["grouping_checked"] and sample["rank_credible"]
    print("Horizon", sample["N"], "retained indices", (1,sample["N"]-1), "common rank", kept[0], "coverage max", max(sample["coverage_residuals"]))
print("Fixed exclusions: (1,1); absolute threshold 1e-4; no matrix rescaling.")
print("Finite-sample rank evidence only. Analytic full-PEP and Lyapunov proofs remain unresolved.")""")
)
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum")
)
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Identify the vectors")
)
nb.cells[start:end] = cells
nbf.write(nb, path)
km = KernelManager(
    kernel_name="attempt-python",
    kernel_spec_manager=KernelSpecManager(
        kernel_dirs=[str(root / "supplementary/.runtime/kernels")]
    ),
)
NotebookClient(
    nb, timeout=120, km=km, resources={"metadata": {"path": str(root)}}
).execute()
nbf.write(nb, path)
for c in nb.cells:
    if c.cell_type == "markdown":
        assert "\\(" not in c.source and "\\[" not in c.source
        assert not any(ord(x) < 32 and x not in "\n\t" for x in c.source)
record = {
    "status": "passed",
    "fresh_kernel": True,
    "source_math_checks": "passed",
    "rendered_review": "omitted by evaluation-ancillary-v1",
    "notebook_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
}
(root / "supplementary/b3-notebook-execution.json").write_text(
    json.dumps(record, indent=2)
)
check = root / "supplementary/dual_feg_example_lyap_checklist.md"
lines = check.read_text(encoding="utf-8-sig").splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B3"
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + record["notebook_sha256"]
    if line.startswith("| 9."):
        lines[i] = (
            "| 9. partial-sum Lyapunov construction and rank profile | verified | 13–18 | Recomputed certificate; visible grouping and coverage checks; confirmed rank 4 at N=4,6 with fixed exclusions. |"
        )
    for number, cell in [(10, 19), (11, 20), (12, 21)]:
        if line.startswith(f"| {number}."):
            parts = line.split("|")
            parts[3] = f" {cell} "
            lines[i] = "|".join(parts)
check.write_text("\n".join(lines), encoding="utf-8")
print("B3 notebook executed and source-checked.")
