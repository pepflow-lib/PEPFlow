# /lyap-vectors: PEPFlow Block 4 — Identifying Special Vectors

Using the Lyapunov partial sums from Block 3, find which special vectors span each V_k and extract the coefficient pattern as a function of k.

> $ARGUMENTS  (ALGO_NAME, e.g. `heavy_ball`)

---

## Environment

PEPFlow repo root: `$(git rev-parse --show-toplevel)/`
Python executable: `.venv/bin/python3`
Input: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json`
Output: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json`
Notebook: update `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb`

---

## Reference Scope

When looking for reference examples, notebook structure, proof-writing patterns, or prompt skeletons, use only files under `examples_peppy/`. The `examples_peppy/_references/` subtree is explicitly allowed and may be used freely as reference material. Do not inspect or follow other repository example/reference files outside `examples_peppy/` for this workflow.

---

## Step 1 — Load State and Rebuild Partial Sums

Recreate the PEP context and reconstruct the `lyap` list using the grouping code from Block 3:

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import pepflow as pf, numpy as np, sympy as sp, importlib.util, json
from pepflow.lyapunov_utils import (
    vectors_in_column_space, find_symmetric_coefficient_matrix,
    find_basis_with_sparsest_coefficients, select_independent_subset,
)

with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json") as fh:
    b3 = json.load(fh)

N_int = b3["N_verify"]
N = sp.S(N_int)
params_sp = {k: sp.Rational(str(v)) if isinstance(v, (int, float)) else sp.S(v)
             for k, v in json.loads(b3["params_json"]).items()}

spec = importlib.util.spec_from_file_location("setup",
    "examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
ctx, pb, obj = mod.get_pep_setup(N, params_sp)
result = pb.solve(resolve_parameters=params_sp)
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)

row_names = b3["lambda_row_names"]
col_names = b3["lambda_col_names"]
lamb_mat  = np.array(b3["lambda_matrix"])
extra_duals = b3.get("extra_duals", {})

def idx(tag, N=N_int):
    s = tag.split("_")[1]
    return int(s) if s.isdigit() else N + 1

def lamb_val(ri, ci):
    i = row_names.index(ri); j = col_names.index(ci)
    return float(lamb_mat[i, j])

# Reconstruct lyap using grouping_code from Block 3
# (paste the verified grouping code here)
exec(b3["grouping_code"])

ranks = [int(np.linalg.matrix_rank(
    pm.eval_scalar(Vk).inner_prod_coords.astype(float), tol=1e-4))
    for Vk in lyap]
print("Rank profile (sanity check):", ranks)
EOF
```

Confirm the rank profile matches what was stored in Block 3.

---

## Step 2 — Build Candidate Special Vectors

Create a rich candidate set from all tagged vectors, basis vectors, and their pairwise differences:

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
# (continuing — lyap, ctx, pm, params_sp available)
from itertools import combinations

# Start with basis vectors and all tagged iterates
candidates = list(ctx.basis_vectors())
for tag in [f"x_{i}" for i in range(N_int + 1)] + ["x_star", "y_0"]:
    v = ctx.get(tag, None)
    if v is not None and v not in candidates:
        candidates.append(v)

# Optionally add gradient evaluations if obj is a function:
# for i in range(N_int + 1):
#     xi = ctx.get(f"x_{i}")
#     if xi is not None:
#         try: candidates.append(obj.grad(xi))
#         except: pass

# Pairwise differences
base = list(candidates)
for i, j in combinations(range(len(base)), 2):
    candidates.append(base[i] - base[j])

print(f"Total candidates: {len(candidates)}")
print("Candidate labels:", [str(v) for v in candidates[:20]], "...")
EOF
```

If the problem has domain-specific vectors (e.g., auxiliary iterates `z_k`), add them explicitly to the initial set. The user may suggest additional candidates via the optional argument to this command.

---

## Step 3 — Filter to Column Space of Each V_k

For each k (excluding k=0 and k=N since those may be degenerate), first identify which candidates lie in `col(V_k)`. Then use `find_basis_with_sparsest_coefficients` to choose a rank-spanning subset whose quadratic coefficient matrix is as sparse as possible. The basis is not unique; this step picks a reproducible, interpretable coordinate system rather than a canonical mathematical basis.

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
# (continuing — lyap, candidates, pm, ctx, params_sp available)

from pepflow.lyapunov_utils import find_basis_with_sparsest_coefficients

spanning_by_k = {}
basis_by_k = {}
coeff_by_k = {}
for k in range(1, N_int):
    rank_k = int(np.linalg.matrix_rank(
        pm.eval_scalar(lyap[k]).inner_prod_coords.astype(float), tol=1e-4))
    if rank_k == 0:
        spanning_by_k[k] = []
        basis_by_k[k] = []
        continue

    in_col = vectors_in_column_space(
        lyap[k], candidates,
        pep_context=ctx, resolve_parameters=params_sp,
        rtol=1e-4, atol=1e-4,
    )
    spanning_by_k[k] = in_col
    print(f"V_{k} (rank {rank_k}): [{', '.join(str(v) for v in in_col)}]")

    # Among all independent rank_k-sized subsets of the column-space candidates,
    # choose one whose decomposition has the most near-zero coefficients.
    # This tends to expose the simplest Lyapunov vector pattern.
    basis, C = find_basis_with_sparsest_coefficients(
        lyap[k],
        in_col,
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=1e-6,
        indep_tol=1e-7,
    )
    if len(basis) != rank_k:
        print(f"  WARNING: selected {len(basis)} vectors but rank is {rank_k}")

    basis_by_k[k] = basis
    coeff_by_k[k] = C
    labels = [str(v) for v in basis]
    zeros = int(np.sum(np.abs(C) < 1e-6)) if C.size else 0
    print(f"  sparse basis: {labels}")
    print(f"  zero coefficients: {zeros}/{C.size}")
EOF
```

Interpret the result in two layers:

1. `spanning_by_k[k]` is the full list of candidate vectors that lie in `col(V_k)`.
2. `basis_by_k[k]` is one selected basis: it has `rank(V_k)` independent vectors and gives a sparse symmetric decomposition of the quadratic part of `V_k`.

Look for a **k-dependent pattern** in `basis_by_k`, not only in the larger column-space list. Common patterns:
- `[x_0 − x_star, grad_f(x_k), x_{k+1} − x_star]` (GD-like, 3 vectors)
- `[A(x_N), y_0 − x_N]` (APPM-like, 2 constant vectors)
- Pattern with `x_{k+1}` shifting as k increases

**Check linear independence**: Make sure to check that the vectors corresponding to the conjectured pattern are linearly independent. Otherwise, the proposed set is degenerate. If the sparse basis is awkward but another independent subset gives a clearer algorithmic pattern, it is acceptable to use the clearer subset, but record the reason and verify its decomposition residual in Step 5.

**Optional fixed anchors**: If recurrence structure strongly suggests that certain vectors must appear, pass them through `fixed_vectors`:

```python
fixed = [ctx["x_0"] - ctx["x_star"]]
basis, C = find_basis_with_sparsest_coefficients(
    lyap[k], in_col,
    pep_context=ctx, resolve_parameters=params_sp,
    fixed_vectors=fixed,
    zero_tol=1e-6, indep_tol=1e-7,
)
```

Use fixed anchors sparingly: they should encode a real structural guess, not force a desired answer.

**Nontrivial checkpoint**: If the column-space sets are inconsistent across k (no clear pattern), or if the rank is not fulfilled by any combination of candidates:
1. Print the full spanning sets for k=1, 2, 3.
2. Print the sparse bases and zero-counts chosen by `find_basis_with_sparsest_coefficients`.
3. Ask the user whether an auxiliary sequence (e.g., a running sum) might be needed to express V_k.
Do not proceed to Step 4 until a consistent basis hypothesis is identified.

---

## Step 4 — Automated Template Inference

There is currently no maintained automatic `infer_k_dependent_basis_templates` helper in `pepflow.lyapunov_utils`.
If the sparse bases from Step 3 suggest a consistent k-indexed pattern, encode that pattern manually and verify it in Step 5:

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
# (continuing — lyap, basis_by_k, ctx, params_sp available)
# Manually encode the inferred pattern after inspecting Step 3.
def V_k_basis(k):
    # Example (GD-like):
    # return [ctx["x_0"] - ctx["x_star"], obj.grad(ctx[f"x_{k}"]), ctx[f"x_{k+1}"] - ctx["x_star"]]
    return basis_by_k.get(k, [])

for k in range(1, N_int):
    vecs = V_k_basis(k)
    print(f"  k={k}: {[str(v) for v in vecs]}")
EOF
```

If the manually encoded pattern is consistent, proceed to Step 5 using this pattern.
Again, the vectors consisting the conjectured pattern should be linearly independent.

---

## Step 5 — Extract Coefficient Matrices

For each k, compute the coefficient matrix `C[k]` expressing `V_k = Σ_{ij} C[i,j] * v_i * v_j^T`:

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
# (continuing — lyap, basis_by_k, ctx, params_sp available)
import fractions

def V_k_basis(k):
    # Use basis_by_k[k], or encode the manually identified pattern here:
    # Example (GD-like):
    #   return [ctx["x_0"] - ctx["x_star"], obj.grad(ctx[f"x_{k}"]), ctx[f"x_{k+1}"] - ctx["x_star"]]
    return basis_by_k.get(k, [])

coeff_by_k = {}
for k in range(1, N_int):
    basis = V_k_basis(k)
    if not basis:
        print(f"k={k}: no basis — skip")
        continue
    try:
        C = find_symmetric_coefficient_matrix(
            lyap[k], basis, pep_context=ctx, resolve_parameters=params_sp)
        coeff_by_k[k] = C
        labels = [str(v) for v in basis]
        print(f"k={k}:")
        for i in range(C.shape[0]):
            for j in range(i, C.shape[1]):
                if abs(C[i,j]) > 1e-6:
                    frac = fractions.Fraction(float(C[i,j])).limit_denominator(1000)
                    print(f"  C[{labels[i]}, {labels[j]}] = {C[i,j]:.6f}  ≈  {frac}")
    except ValueError as e:
        print(f"k={k}: {e}")
EOF
```

---

## Step 6 — Identify Coefficient Pattern

From the printed fractions, identify how each coefficient depends on `k` (and `N`):
- Constant → `C[i,j] = c`
- Linear in k → `C[i,j] = a*k + b` (fit with k=1,2,3 values)
- Quadratic → `C[i,j] = a*k² + b*k + c`
- Inverses of the above → `1 / C[i,j]` is linear or quadratic

Encode the pattern as a function `coeff_pattern(k, N)` and verify it reproduces all `coeff_by_k[k]` values within tolerance.

**Nontrivial checkpoint**: If the coefficients or their inverse don't follow a clean polynomial pattern in k (e.g., the fractions look random or inconsistent), print all coefficient values and ask the user for insight on the pattern.

---

## Step 7 — Save State

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import json, numpy as np, os
os.makedirs("examples_peppy/{ALGO_NAME}/state", exist_ok=True)

b3 = json.load(open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json"))

# Serialize coefficient matrices (nested list per k)
coeff_by_k_serial = {str(k): C.tolist() for k, C in coeff_by_k.items()}

# Encode the basis template as Python source code
basis_code = """
def V_k_basis(k):
    # TODO: paste finalized basis definition here
    # Example:
    # return [ctx["x_0"] - ctx["x_star"], obj.grad(ctx[f"x_{k}"]), ctx[f"x_{k+1}"] - ctx["x_star"]]
    return basis_by_k.get(k, [])
"""

# Encode coefficient pattern as Python source code
coeff_code = """
def coeff_pattern(k, N):
    # TODO: paste closed-form coefficient formulas here (as dict of (i,j) -> expr)
    # Example: return {(0,0): k/(2*N+1), (1,1): 1/(2*N+1-k), ...}
    return {}
"""

state = {
    **b3,
    "basis_templates": templates if 'templates' in dir() else [],
    "basis_code": basis_code,
    "coeff_by_k": coeff_by_k_serial,
    "coeff_code": coeff_code,
}
with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json", "w") as fh:
    json.dump(state, fh, indent=2)
print("State saved to examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json")
EOF
```

---

## Step 8 — Update Lyapunov Notebook

Open the existing notebook and add or replace the special-vector and coefficient sections with this structure:

1. `## Identify the vectors composing the Lyapunov function`
   - A short markdown cell explaining that Block 4 starts from the Block 3 partial sums and searches for interpretable rank-spanning vectors.
   - A code cell that rebuilds or sanity-checks the rank profile against Block 3.
2. `### Candidate-vector scan`
   - A markdown cell describing the candidate families used: tagged iterates, operator/gradient values, point-to-solution gaps, anchor gaps, meaningful auxiliary sums, and any terminal square/vector suggested by Block 2.
   - A code cell that constructs labeled candidate pairs `(label, vector)`.
   - Remove duplicate candidates by evaluated coordinates, and skip the zero vector so the scan output stays readable.
   - Prefer labels for meaningful derived vectors (for example `q_k`) before labels for algebraically equivalent incidental vectors.
   - A separate code cell that filters candidates to `col(V_k)` and prints:
     ```
     V_k column-space candidates:
        label_1
        label_2
     ```
3. `### Selected basis pattern`
   - A markdown cell stating the inferred rank-spanning template as a displayed formula, including any special terminal/boundary case.
   - A code cell defining `V_k_basis(k)` and `V_k_basis_labels(k)`, then printing the independence check in the compact form:
     ```
     k=1: rank r basis [...]
     ```
4. `### Coefficient matrices`
   - A markdown cell stating the basis order used for interior and terminal cases.
   - A code cell defining `coeff_pattern(k, N)`, decomposing every useful `V_k`, printing a formula residual per `k`, and displaying each coefficient matrix with `pf.pprint_labeled_matrix`.
5. `### Block 4 conclusion`
   - A markdown cell stating the current closed-form `V_k` candidate and noting that Block 5 will symbolically verify the step, base, and boundary identities.

When displaying coefficient matrices in the notebook, use `pf.pprint_labeled_matrix(C, basis_labels, basis_labels, ...)` or an equivalent labeled matrix display. Avoid manual nested-loop row prints such as `print(["1/2", "-1/4"])`; those are hard for users to scan and detach coefficients from their basis vectors.

Do not expose the JSON persistence step for `{ALGO_NAME}_b4.json` as notebook content. The notebook should show the basis discovery, coefficient matrices, pattern, and Lyapunov formula; writing the state file is command/workflow machinery and should happen outside the notebook, or inside a helper invoked by the command script. Avoid even a visible `save_block4_state(...)` notebook cell unless the save operation itself is part of the user's reasoning task.

Do not defer these cells to Block 5; Block 5 should refine and verify them, not create the whole diagnostic trail for the first time.

---

## Output

Report:
- The basis template for V_k (k-indexed pattern of special vectors)
- The coefficient matrix `C[k]` for each k (as a table of fractions)
- The guessed coefficient formula as a function of k and N

- Confirmation that the notebook was updated through the vector/coefficient sections

**Next step**: `/lyap-closed-form {ALGO_NAME}`
