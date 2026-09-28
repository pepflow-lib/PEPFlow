import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

root = Path.cwd().resolve()
assert root.name == "validation" and root.parent.name == "feg_r04"
for name in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "MPLCONFIGDIR",
    "XDG_CACHE_HOME",
):
    p = root / ".review_runtime" / name.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[name] = str(p)
os.environ["MPLBACKEND"] = "Agg"
sys.path[:0] = [
    str(root / "supplementary/approved"),
    str(root / "supplementary/helpers"),
    str(root),
]
nb = json.loads((root / "feg_example_lyap.ipynb").read_text(encoding="utf-8"))
env = {"__name__": "__main__"}
done = []
with (
    (root / "replay-output.txt").open("w", encoding="utf-8") as out,
    redirect_stdout(out),
):
    for c in nb["cells"]:
        if c["cell_type"] != "code" or c["id"] == "47634a7b":
            continue
        print("CELL", c["id"], flush=True)
        exec(compile("".join(c["source"]), c["id"], "exec"), env)
        done.append(c["id"])
    result = dict(
        executed_cells=done,
        omitted_plot_cell="47634a7b",
        certificate=env["checks"],
        ranks_N6=env["ranks"],
        singular_values_N6=env["singular_values"],
        coverage_N6=env["coverage_residuals"],
        basis_count=len(env["candidates"]),
        reconstruction=env["component_residuals"],
        quadratic_residuals=env["coefficient_residuals"],
        step=env["step_check"],
        base=env["base_check"],
        boundary=env["boundary_check"],
    )
    env["certificate"] = json.loads(
        (root / "supplementary/b2-certificate-N4.json").read_text()
    )
    for name in ("b3_certificate_check.py", "b3_decomposition.py", "b3_grouping.py"):
        exec(
            compile(
                (root / "supplementary" / name).read_text(encoding="utf-8-sig"),
                name,
                "exec",
            ),
            env,
        )
    result.update(
        certificate_N4=env["certificate_checks"],
        ranks_N4=env["ranks"],
        singular_values_N4=env["singular_values"],
        coverage_N4=env["coverage_residuals"],
    )
(root / "replay-results.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)
print(
    "Replay completed:", len(done), "notebook code cells and N4 certificate/grouping."
)
