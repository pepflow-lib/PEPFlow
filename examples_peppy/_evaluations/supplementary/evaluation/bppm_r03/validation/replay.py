# Notebook cells and source fragments executed below supply these globals.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import contextlib
import json
import os
import sys
from pathlib import Path

root = Path.cwd()
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
    "JUPYTER_PATH",
):
    p = root / "runtime" / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
sys.path.insert(0, str(root / "supplementary/helpers"))
import bppm_setup as setup  # ty: ignore[unresolved-import]  # Runtime bootstrap adds the archived helper directory to sys.path.  # noqa: E402 -- Initialize paths and runtime environment before importing.
import certificate as api  # ty: ignore[unresolved-import]  # Runtime bootstrap adds the archived helper directory to sys.path.  # noqa: E402 -- Initialize paths and runtime environment before importing.
import runtime  # ty: ignore[unresolved-import]  # Runtime bootstrap adds the archived helper directory to sys.path.  # noqa: E402 -- Initialize paths and runtime environment before importing.

import pepflow as pf  # noqa: E402 -- Initialize paths and runtime environment before importing.

notebook_dir = root
REPO_ROOT = runtime.APPROVED
result = {}
with (
    (root / "replay-output.txt").open("w", encoding="utf-8") as out,
    contextlib.redirect_stdout(out),
):
    for horizon, certpath, densepath in [
        (6, "supplementary/b2-N6-certificate.json", "supplementary/b2-N6-dense.json"),
        (4, "state/bppm_b4.json", "state/bppm_dense.json"),
    ]:
        certificate = json.loads((root / certpath).read_text())
        N_int = horizon
        params_sp = json.loads(certificate["params_json"])
        ctx, pb, obj = setup.get_pep_setup(N_int, params_sp)
        pb.set_relaxed_constraints(certificate["relaxed_constraints"])
        for name in ("certificate_check", "decomposition", "grouping"):
            exec(
                compile(
                    (root / f"supplementary/b3_{name}.py").read_text(
                        encoding="utf-8-sig"
                    ),
                    name,
                    "exec",
                )
            )
        dense = json.loads((root / densepath).read_text())
        actual = api.verify(ctx, pb, params_sp, certificate, dense["opt_value"])
        increments = []
        for k in range(N_int):
            inc = sum(
                (
                    group_terms[name]
                    for name, target in term_assignment.items()
                    if target == k
                ),
                pf.Scalar.zero(),
            )
            v = pm.eval_scalar(lyap[k + 1] - lyap[k] - inc)
            increments.append(
                [
                    api.max_abs(v.inner_prod_coords),
                    api.max_abs(v.func_coords),
                    api.max_abs(v.offset),
                ]
            )
        result[str(horizon)] = {
            "certificate_id": certificate["certificate_id"],
            "checks": actual,
            "rank_profile": ranks,
            "singular_values": singular_values,
            "coverage_errors": coverage_errors,
            "increment_errors": increments,
            "rank_credible": rank_credible,
        }
    for name in ("scan", "search", "basis", "coefficients", "structure"):
        exec(
            compile(
                (root / f"supplementary/b4_{name}.py").read_text(encoding="utf-8-sig"),
                name,
                "exec",
            )
        )
    result["B4"] = {
        "quadratic_residuals": coefficient_residuals,
        "component_residuals": component_residuals,
        "search": sparse_search_results,
    }
    for name in ("common", "step", "base", "boundary"):
        exec(
            compile(
                (root / f"supplementary/b5_{name}.py").read_text(encoding="utf-8-sig"),
                name,
                "exec",
            )
        )
    result["B5"] = {
        "step": step_check,
        "base": base_check,
        "boundary": boundary_check,
        "multipliers": {str(k): str(v) for k, v in expected.items()},
    }
(root / "replay-results.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)
print("Replayed B2/B3 N=4,6, B4 all indices and B5 exact symbolic checks successfully.")
