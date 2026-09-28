import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "supplementary" / ".runtime"
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
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
):
    folder = RUNTIME / key.lower()
    folder.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(folder)
os.environ["JUPYTER_PATH"] = str(RUNTIME / "jupyter")
import nbformat as nbf  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
from nbclient import (  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
    NotebookClient,
)

results = json.loads((ROOT / "supplementary" / "_sweep_tmp.json").read_text())
state = dict(
    algo_name="feg",
    problem_type="monotone_operator",
    obj_tag="A",
    params_json='{"L": 1, "R": 1}',
    performance_metric="||A(x_N)||^2",
    initial_condition="||x_0-x_star||^2 <= R^2",
    conjectured_rate="4*L**2*R**2/N**2",
    setup_file="feg_setup.py",
    sweep_results=results,
    N_verify=4,
    analytic_status="unproved",
    first_horizon_value="2*L**2*R**2",
)
(ROOT / "state").mkdir(exist_ok=True)
(ROOT / "state" / "feg_b1.json").write_text(json.dumps(state, indent=2))
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
nb = nbf.v4.new_notebook()
nb.cells = [
    md(r"""# FEG: residual convergence for monotone Lipschitz operators
Let $A$ be a monotone, $L$-Lipschitz operator on a finite-dimensional real Euclidean space, with $L>0$, $A(x_\star)=0$, and $\|x_0-x_\star\|^2\le R^2$, where $R\ge0$. For integers $k=0,\ldots,N-1$, run
$$x_{k+1/2}=x_k+\frac{x_0-x_k}{k+1}-\frac{k}{(k+1)L}A(x_k),$$
$$x_{k+1}=x_k+\frac{x_0-x_k}{k+1}-\frac1L A(x_{k+1/2}).$$
At $k=0$, $x_{1/2}=x_0$ is the same point. The performance metric is $\|A(x_N)\|^2$ for integers $N\ge1$.
"""),
    md(
        "## Theorem and proof\nPending Blocks 2–5. Numerical evidence below is not an arbitrary-horizon proof."
    ),
    code("""from pathlib import Path
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
notebook_dir = Path.cwd().resolve()
repo_root = notebook_dir / "supplementary" / "approved"
sys.path.insert(0, str(repo_root))
import pepflow as pf
import sympy as sp
print("Approved framework:", pf.__file__)"""),
]
setup = (ROOT / "feg_setup.py").read_text()
start = setup.index("L = pf.Parameter")
split = setup.index("def make_ctx_feg")
nb.cells.extend(
    [
        md("## Operator and parameter definitions"),
        code(setup[start:split].strip()),
        md("## Algorithm and PEP setup"),
        code(setup[split:].strip()),
        code("""ctx_check, pb_check, _ = get_pep_setup(2, {"L": 1, "R": 1})
assert ctx_check["x_0"] is ctx_check["x_1/2"]
print("Shared first half-step confirmed; squared residual and R² normalization encoded.")"""),
        md("## Numerical evidence"),
        code("""results = json.loads((notebook_dir / "state" / "feg_b1.json").read_text())["sweep_results"]
horizons = np.array([row["N"] for row in results])
values = np.array([row["opt_value"] for row in results])
for row in results:
    print(f'N={row["N"]}: {row["opt_value"]:.10f} ({row["status"]})')
candidate = 4.0 / horizons**2
print("Maximum residual for N >= 2:", np.max(np.abs(values[1:] - candidate[1:])))
fig, ax = plt.subplots()
ax.plot(horizons, values, "o-", label="PEP, L=R=1")
ax.plot(horizons, candidate, "--", label="Candidate 4/N²")
ax.set(xlabel="N", ylabel="Squared operator residual")
ax.legend()
ax.grid(True)
plt.show()"""),
        md(
            r"""The conjectured bound is $\|A(x_N)\|^2\le4L^2R^2/N^2$. The sweep agrees for $N=2,\ldots,7$; at $N=1$ the PEP gives $2L^2R^2$, below this bound. Homogeneous rescaling supplies the displayed $L^2R^2$ factor. All seven solves used CLARABEL defaults and returned optimal. Proof and sharpness for arbitrary horizons remain unresolved."""
        ),
    ]
)
for title in [
    "Dense and relaxed proof solves",
    "Lambda and S verification",
    "Partial-sum Lyapunov construction and rank profile",
    "Identify the vectors composing the Lyapunov function",
    "Coefficient extraction and closed-form V_k",
    "Symbolic step, base, and boundary identities",
]:
    nb.cells.append(md("## " + title + "\nPending the corresponding later block."))
bootstrap, imports = nb.cells[2].source.split("import pepflow as pf", 1)
nb.cells[2].source = bootstrap
nb.cells.insert(3, code("import pepflow as pf" + imports))
nb.metadata["kernelspec"] = dict(
    name="feg-private", display_name="FEG pinned Python", language="python"
)
kdir = RUNTIME / "jupyter" / "kernels" / "feg-private"
kdir.mkdir(parents=True, exist_ok=True)
(kdir / "kernel.json").write_text(
    json.dumps(
        dict(
            argv=[
                sys.executable,
                "-I",
                "-B",
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            display_name="FEG pinned Python",
            language="python",
        )
    )
)
path = ROOT / "feg_example_lyap.ipynb"
nbf.write(nb, path)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="feg-private",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nbf.write(nb, path)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert all(ord(ch) >= 32 or ch in "\n\t" for ch in cell.source)
    for output in cell.get("outputs", []):
        assert output.output_type != "error"
items = [
    (
        "title, problem description, and the algorithm update equations in LaTeX",
        "verified",
        "0",
        "Assumptions, metric, both recurrences and shared first half-step; delimiter/control-character checks passed.",
    ),
    (
        "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
        "pending",
        "1",
        "Theorem deliberately pending B5.",
    ),
    ("imports", "verified", "2", "Executed with approved framework origin."),
    (
        "function/operator definitions",
        "verified",
        "4",
        "LipschitzMonotoneOperator and L,R definitions executed.",
    ),
    (
        "make_ctx_feg and get_pep_setup",
        "verified",
        "6,7",
        "Visible exact recurrence, R² normalization, metric; shared-point assertion passed.",
    ),
    (
        "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
        "verified",
        "9,10",
        "Seven cached optimal results printed; matplotlib PNG output present; numerical residual checked.",
    ),
    ("dense and relaxed proof solves", "pending", "11", "B2"),
    (
        "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
        "pending",
        "12",
        "B2",
    ),
    ("partial-sum Lyapunov construction and rank profile", "pending", "13", "B3"),
    ("special-vector identification", "pending", "14", "B4"),
    ("coefficient extraction and closed-form V_k", "pending", "15", "B4/B5"),
    ("symbolic step, base, and boundary identities", "pending", "16", "B5"),
]
assert any("image/png" in output.get("data", {}) for output in nb.cells[10].outputs)
text = f"Notebook: {path.name}\nLast reviewed block: B1\nSHA-256: {hashlib.sha256(path.read_bytes()).hexdigest()}\nPresentation policy: evaluation-ancillary-v1; no rendered/image inspection performed.\n\n| Item | Requirement | Status | Cells | Evidence |\n|---|---|---|---|---|\n"
for i, (label, status, cells, evidence) in enumerate(items, 1):
    cells = ",".join(
        str(int(c) + 1 if int(c) >= 3 else int(c)) for c in cells.split(",")
    )
    if i == 3:
        cells = "2,3"
    text += f"| {i} | {label} | {status} | {cells} | {evidence} |\n"
(ROOT / "supplementary" / "feg_example_lyap_checklist.md").write_text(text)
print(
    json.dumps(
        dict(
            notebook=str(path),
            code_cells_executed=sum(c.cell_type == "code" for c in nb.cells),
            max_rate_residual=max(
                abs(r["opt_value"] - 4 / r["N"] ** 2) for r in results[1:]
            ),
            presentation_policy="evaluation-ancillary-v1",
        )
    )
)
