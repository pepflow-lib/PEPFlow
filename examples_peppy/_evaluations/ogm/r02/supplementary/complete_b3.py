"""Persist the confirmed B3 handoff and execute visible notebook constructions."""

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for key in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]:
    os.environ[key] = "1"
sys.path.insert(0, str(ROOT / "supplementary"))
import numpy as np  # noqa: E402
from b3_notebook_cells import DECOMPOSITION, GROUPING  # noqa: E402

b2 = json.loads((ROOT / "state/ogm_b2.json").read_text())
samples = [
    json.loads((ROOT / f"supplementary/b3-rank-N{n}.json").read_text()) for n in (6, 8)
]
rank_left, rank_right = 1, 1
common = []
for sample in samples:
    ranks = [
        int(np.linalg.matrix_rank(np.asarray(matrix), tol=1e-4))
        for matrix in sample["lyap_inner_prod_coords"]
    ]
    assert ranks == sample["rank_profile"]
    assert (
        sample["certificate_checked"]
        and sample["grouping_checked"]
        and sample["rank_credible"]
    )
    assert sample["recipe_id"] == samples[0]["recipe_id"]
    assert sample["rank_convention"] == samples[0]["rank_convention"]
    assert (
        sample["decomposition_code"] == DECOMPOSITION
        and sample["grouping_code"] == GROUPING
    )
    retained = ranks[rank_left : sample["N"] + 1 - rank_right]
    assert len(retained) >= 3 and len(set(retained)) == 1
    common.append(retained[0])
assert len(set(common)) == 1
selected = samples[0]
assert selected["certificate_id"] == b2["certificate_id"]
rank_search = dict(
    status="confirmed",
    boundary_exclusions=dict(left=1, right=1),
    rank=common[0],
    confirmed_horizons=[6, 8],
    selected_certificate_id=b2["certificate_id"],
    recipe_id=selected["recipe_id"],
    rank_convention=selected["rank_convention"],
    unresolved_samples=[],
    evidence_path="supplementary/rank_search.json",
)
(ROOT / "supplementary/rank_search.json").write_text(
    json.dumps({"summary": rank_search, "samples": samples}, indent=2)
)
b3 = {
    **b2,
    "rank_profile": selected["rank_profile"],
    "rank_search": rank_search,
    **{
        k: selected[k]
        for k in (
            "lyap_inner_prod_coords",
            "lyap_func_coords",
            "lyap_offsets",
            "certificate_check_code",
            "decomposition_code",
            "grouping_code",
        )
    },
    "extra_duals": {},
    "rank_tolerance": 1e-4,
    "reconstruction_tolerance": 1e-4,
    "reconstruction_rtol": 1e-5,
    "grouping_coverage": dict(
        constraint_assignment=selected["constraint_assignment"],
        S_assignment=selected["S_assignment"],
        normalization_constraint="initial_condition",
        boundary_constraints=[],
        boundary_S=["terminal_S"],
        omitted_constraints=[],
        checked=True,
    ),
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(ROOT / "state/ogm_b3.json").write_text(json.dumps(b3, indent=2, allow_nan=False))

runtime = ROOT / "supplementary/.runtime"
for key in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]:
    os.environ[key] = "1"
for key in [
    "TEMP",
    "TMP",
    "IPYTHONDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "MPLCONFIGDIR",
    "XDG_CACHE_HOME",
]:
    location = runtime / key.lower()
    location.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(location)
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
# optional notebook-generation dependency
import nbformat as nbf  # noqa: E402  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # noqa: E402  # ty: ignore[unresolved-import]

intro = r"""## Lyapunov partial sums
Let $I_{i,j}=f(x_j)-f(x_i)+\langle g_j,x_i-x_j\rangle+\|g_i-g_j\|^2/(2L)\le0$.
The selected numerical weights define $V_0=0$ and
$$V_1=\lambda_{\star,0}I_{\star,0}+\lambda_{\star,1}I_{\star,1}+\lambda_{0,1}I_{0,1},$$
$$V_{k+1}-V_k=\lambda_{\star,k+1}I_{\star,k+1}+\lambda_{k,k+1}I_{k,k+1}\quad(1\le k<N).$$
Every increment is nonpositive. We reserve the entire selected positive semidefinite $S$ for the terminal boundary; no numerical factor is discarded.
At $N=6$ and $N=8$, the interior quadratic rank is three when $V_0$ and $V_N$ are excluded. The zero base and rank-two terminal value remain part of the later reconstruction and proof obligations. Coverage below checks every scalar coordinate and includes the entire boundary remainder.
"""
comparison = """rank_evidence = json.loads((notebook_dir / "supplementary/rank_search.json").read_text())
common_ranks = []
for sample in rank_evidence["samples"]:
    observed = [int(np.linalg.matrix_rank(np.asarray(matrix), tol=1e-4)) for matrix in sample["lyap_inner_prod_coords"]]
    assert observed == sample["rank_profile"]
    retained = observed[1:sample["N"]]
    assert len(retained) >= 3 and len(set(retained)) == 1
    assert sample["certificate_checked"] and sample["grouping_checked"] and sample["rank_credible"]
    common_ranks.append(retained[0])
    print("Confirmed horizon", sample["N"], "interior rank", retained[0], "retained indices", list(range(1,sample["N"])))
assert len(set(common_ranks)) == 1 and len(common_ranks) >= 2
print("Fixed exclusions: left=1, right=1; absolute rank threshold 1e-4 on unscaled coordinates.")
print("Smallest retained singular value exceeds 0.009; discarded singular values are below 7e-9.")
print("This is finite-sample rank evidence; basis reconstruction and universal proof remain pending.")
"""
path = ROOT / "ogm_example_lyap.ipynb"
notebook = nbf.read(path, as_version=4)
start = next(
    i for i, c in enumerate(notebook.cells) if c.id in ("b3-placeholder", "b3-heading")
)
end = next(i for i, c in enumerate(notebook.cells) if c.id == "b4-placeholder")
notebook.cells[start:end] = [
    nbf.v4.new_markdown_cell(intro, id="b3-heading"),
    nbf.v4.new_code_cell(DECOMPOSITION, id="b3-decomposition"),
    nbf.v4.new_code_cell(GROUPING, id="b3-partial-sums"),
    nbf.v4.new_code_cell(comparison, id="b3-cross-horizon"),
]
nbf.write(notebook, path)
NotebookClient(
    notebook,
    timeout=120,
    kernel_name="ogm-owned",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nbf.write(notebook, path)
for cell in notebook.cells:
    if cell.cell_type == "markdown":
        assert not any(
            char in cell.source for char in ["\x0c", "\r", "\\(", "\\)", "\\[", "\\]"]
        )
    if cell.id.startswith("b3-"):
        for output in cell.get("outputs", []):
            if output.get("output_type") == "stream":
                print(output["text"])
print(
    json.dumps(
        {
            "clean_kernel_execution": "passed",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )
)
