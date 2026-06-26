# /lyap-define: PEPFlow Block 3 — Defining the Lyapunov Function

Using the Full-PEP dual certificates from Block 2, build partial-sum sequences V_k by accumulating weighted inequalities step by step, and verify a consistent low rank across iterations.

> $ARGUMENTS  (ALGO_NAME, e.g. `heavy_ball`)

---

## Environment

PEPFlow repo root: `$(git rev-parse --show-toplevel)/`
Python executable: `.venv/bin/python3`
Input: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json`
Output: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json`
Notebook: update `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb`

---

## Reference Scope

When looking for reference examples, notebook structure, proof-writing patterns, or prompt skeletons, use only files under `examples_peppy/`. The `examples_peppy/_references/` subtree is explicitly allowed and may be used freely as reference material. Do not inspect or follow other repository example/reference files outside `examples_peppy/` for this workflow.

---

## Step 1 — Load State and Recreate Context

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import pepflow as pf, numpy as np, sympy as sp, importlib.util, json, itertools

with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json") as fh:
    b2 = json.load(fh)

N_int = b2["N_verify"]
N = sp.S(N_int)
params_sp = {k: sp.Rational(str(v)) if isinstance(v, (int, float)) else sp.S(v)
             for k, v in json.loads(b2["params_json"]).items()}

spec = importlib.util.spec_from_file_location("setup",
    "examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
ctx, pb, obj = mod.get_pep_setup(N, params_sp)
result = pb.solve(resolve_parameters=params_sp)
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)

row_names = b2["lambda_row_names"]
col_names = b2["lambda_col_names"]
lamb_mat  = np.array(b2["lambda_matrix"])

def idx(tag, N=N_int):
    s = tag.split("_")[1]
    return int(s) if s.isdigit() else N + 1

def lamb_val(ri, ci):
    i = row_names.index(ri); j = col_names.index(ci)
    return float(lamb_mat[i, j])

print(f"Context loaded: N={N_int}, basis vectors:", [str(v) for v in ctx.basis_vectors()])
print("Non-zero lambda entries:")
for ri in row_names:
    for ci in col_names:
        v = lamb_val(ri, ci)
        if abs(v) > 1e-6:
            print(f"  λ({ri},{ci}) = {v:.6f}")
EOF
```

---

## Step 2 — Extract All Dual Variables

Collect both interpolation duals (from λ matrix) and any additional named constraint duals (e.g., Lipschitz):

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'PYEOF'
# (insert after context creation above)

# Interpolation duals — already in lamb_mat / row_names / col_names

# Extra initial constraint duals (non-interpolation, non-IC):
# Note: PrimalPEPDualVarManager stores named_constraints; DualPEPDualVarManager
# stores named_variables. Inspect whichever mapping is present.
obj_tag = b2["obj_tag"]
extra_duals = {}
name_map = getattr(
    result.dual_var_manager,
    "named_constraints",
    getattr(result.dual_var_manager, "named_variables", {}),
)
for name in name_map:
    if name == "initial_condition":
        continue
    if name.startswith(f"{obj_tag}:"):   # interpolation constraint
        continue
    v = result.dual_var_manager.dual_value(name)
    if v is not None and abs(v) > 1e-6:
        extra_duals[name] = float(v)

print("Extra constraint duals:", extra_duals)
PYEOF
```

If `extra_duals` is non-empty, these must be included in the partial sums below (see Step 3 instructions for Lipschitz-type extras).

---

## Step 3 - Choose the S Decomposition


Before computing a new numerical LDL decomposition, check whether Block 2 or
`examples_peppy/_references/{ALGO_NAME}/` already gives a verified closed-form
or direct decomposition of the Gram dual certificate `S`. If a known
decomposition exists, use it as the authoritative `S` representation in this
block. Do not replace a known proof-specific decomposition with a generic LDL
factorization just because LDL is available.

Common sources to check:

- `{ALGO_NAME}_b2.json` fields such as `S_decomp_type`, `S_formula`, `S_code`,
  or stored direct square families
- notebooks under `examples_peppy/_references/{ALGO_NAME}/`
- a prior proof notebook section that verifies `S_guess` against the relaxed
  certificate matrix

When a reference directory exists, inspect it before computing LDL. Search the
reference notebooks/modules for proof-specific decomposition names and patterns
such as `S_guess`, `S_piece`, `S_decomp`, `square`, `remainder`, `rank V`,
`lyap`, or `partial_sum`. If a reference contains a verified decomposition
(`S_guess` matching the certificate matrix, a sequence of square terms, or a
rank-profile construction that uses named S pieces), adapt that decomposition
into this workflow.

Do not treat the absence of already-serialized per-step fields in
`{ALGO_NAME}_b2.json` as evidence that no known decomposition exists. A reference
notebook may give the proof-specific decomposition only as executable notebook
code, such as `S_guess1 + S_guess2 + ...`; in that case, translate those sums
into named pieces and record the translated code in the new state.

When using a known decomposition, record its per-step pieces explicitly, e.g.
`S_i`, `S_piece[i]`, or another named per-step square/residual term, because Step 4 should
subtract those same pieces when building `V_k`.

Use LDL only after all of the following are true:

1. `{ALGO_NAME}_b2.json` has no usable direct or closed-form S decomposition.
2. No reference notebook/module contains a verified `S_guess`, `S_piece`, or
   equivalent square-term construction.
3. You have explicitly reported that no known decomposition was found, or that
   the known decomposition was tried and is insufficient for constructing the
   partial sums.

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
# (continuing from the context creation script above)
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

S_sol = result.get_gram_dual_matrix()
basis = ctx.basis_vectors()
D, ell = ldl_decompose_with_reversed_basis(S_sol, basis, print_output=False)

n = D.shape[0]
print("D diagonal:", [round(float(D[i,i]),6) for i in range(n)])
print("ell vectors (reversed):", [str(e) for e in ell])
# ell[0] corresponds to the latest iterate term, ell[-1] to the earliest
EOF
```

For cases where `S` is a single squared term or a known sum of squared terms,
skip the LDL computation and carry the known terms forward.

---

## Step 4 — Build Partial Sums V_k

Accumulate dual contributions step by step. The canonical ordering is:

**Sign convention (mandatory)**: Define the partial sums `V_k` so they are
nonincreasing in the final proof under the residual convention used in that
notebook. For the common convention
`I_lip <= 0`, `I_mon <= 0`, and nonnegative dual multipliers, the displayed
increment should have the form

```text
V_{k+1} - V_k = positive_lip * I_lip + positive_mon * I_mon + ...
```

so that `V_{k+1} <= V_k`. If the algebraic identity is zero only after flipping
this direction, flip the definition of `V_k` rather than carrying a
sign-reversed Lyapunov function forward. Do not proceed based only on a zero
residual matrix; explicitly check the telescoping inequality direction and
record the convention in `grouping_code`.

- **Smooth function problems**: at step `j` (j=0..N−1), add:  
  - First add the initial boundary interpolation term `(star, 0)` outside the loop.
  - Inside the loop, add interpolation pairs `(j, j+1)` and `(star, j+1)`.

- **Operator problems**: at step `j`, add the interpolation terms and any extra constraint duals (Lipschitz, etc.) associated with step `j+1`.

- S contribution:
  - If Step 3 found a known/direct S decomposition, subtract the corresponding
    per-step S pieces here. For example, if the reference proof gives
    `S = sum_i S_piece[i]`, then the step-`i` increment should subtract
    `S_piece[i]`, not a newly computed LDL square.
  - Otherwise use the LDL contribution
    `-D[j,j] * ell[N-j]^2` (from LDL, reversed-basis ordering), if applicable.

This preference is important: a proof-specific S decomposition often carries
the interpretable vectors needed by `lyap-vectors` and `lyap-closed-form`.
Generic LDL may verify numerically but can obscure the intended closed-form
Lyapunov structure.

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
# (continuing from Steps 1–3)

lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()

# --- Initial boundary interpolation term ---
for ri in row_names:
    i = idx(ri)
    for ci in col_names:
        j = idx(ci)
        v = lamb_val(ri, ci)
        if abs(v) < 1e-8:
            continue
        if i == N_int + 1 and j == 0:
            partial_sum = partial_sum + v * obj.interp_ineq(ri, ci)

for step in range(N_int):
    # --- S contribution ---
    # Prefer known/direct S pieces from Step 3 when available, for example:
    # partial_sum = partial_sum - S_piece_terms[step]
    # Otherwise uncomment and adapt if using LDL:
    # delta = float(D[step, step]) if step < D.shape[0] else 0.0
    # if abs(delta) > 1e-8:
    #     partial_sum = partial_sum - delta * ell[N_int - step] ** 2

    # --- Interpolation terms ---
    for ri in row_names:
        i = idx(ri)
        for ci in col_names:
            j = idx(ci)
            v = lamb_val(ri, ci)
            if abs(v) < 1e-8:
                continue
            # Include pairs associated with this step:
            if (i == step and j == step + 1) or (i == N_int + 1 and j == step + 1):
                partial_sum = partial_sum + v * obj.interp_ineq(ri, ci)

    # --- Extra constraint duals (Lipschitz, etc.) ---
    # For each extra dual associated with step+1, add here:
    # for name, mu in extra_duals.items():
    #     if parse_step_from_name(name) == step + 1:
    #         partial_sum = partial_sum + mu * build_expr_for(name)

    lyap.append(partial_sum)

# Rank profile
ranks = []
for k, Vk in enumerate(lyap):
    M = pm.eval_scalar(Vk).inner_prod_coords.astype(float)
    rank = int(np.linalg.matrix_rank(M, tol=1e-4))
    ranks.append(rank)
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()

print("Interior rank is constant:", len(set(ranks[1:N_int])) == 1)
EOF
```

---

## Step 5 — Diagnose and Fix Rank Profile

Interpret the rank profile `ranks = [r_0, r_1, ..., r_N]`:

- **Good**: constant rank `r` for `k = 1..N−1`, with potential exceptions at `k = N`
  → each V_k lives in a fixed r-dimensional subspace
- **Growing rank** (rank increases with k): the grouping of constraint terms is wrong
- **Wrong monotonicity direction**: the ranks may look good but the proof direction is
  invalid if the chosen `V_k` is nondecreasing under residuals that are `<= 0`.
  In that case, flip the sign convention for the partial sums and recompute the
  rank profile and boundary coverage before saving state.

**If rank grows**: try reordering/shifting the way constraint duals are grouped. For example, you may add duals for `(j, j+1), (star, j+1)` rather than `(j, j+1), (star, j)`. Rerun Step 4 with the adjusted order.

**Nontrivial checkpoint**: If the rank profile is growing and simple reorderings do not fix it (try at least 3 orderings), print the rank profile and present it to the user. Ask whether any of the V_k's should include an additional term type not yet considered (e.g., a different class of inequalities or a separate auxiliary sequence). Only proceed after agreement on an approach.

---

## Step 6 — Verify Coverage

The final partial sum `lyap[N]` should be expressible using nearly all dual terms from the Full-PEP proof. Check that at most one interpolation inequality and at most one S square term are left out (these become the boundary terms in the final proof):

```bash
.venv/bin/python3 - <<'EOF'
# (continuing from above)
M_final = pm.eval_scalar(lyap[N_int]).inner_prod_coords.astype(float)
rank_final = int(np.linalg.matrix_rank(M_final, tol=1e-4))
print(f"lyap[{N_int}] rank:", rank_final)
print("Coverage check: lyap[N] rank should be 0 or 1 (boundary identity term)")
EOF
```

---

## Step 7 — Save State

Serialize the inner-product coordinates of each V_k (as nested lists) for Block 4.
Also include function coordinates (`func_coords`) if the problem class involves function values.

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
# (continuing from above — lyap list and ranks are available)
import json, os
os.makedirs("examples_peppy/{ALGO_NAME}/state", exist_ok=True)

lyap_coords = []
for k, Vk in enumerate(lyap):
    M = pm.eval_scalar(Vk).inner_prod_coords
    # Convert to plain Python floats to ensure JSON serialization succeeds
    lyap_coords.append([[float(x) for x in row] for row in M])

b2 = json.load(open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json"))

# Build the Python code that reconstructs the partial sums in Block 4.
# This is the grouping logic from Step 4 (with any corrections from Step 5).
grouping_code = """
# Partial sum grouping code — paste verified version from lyap-define Step 4/5
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for step in range(N_int):
    # TODO: insert verified grouping logic here
    lyap.append(partial_sum)
"""

state = {
    **b2,
    "rank_profile": ranks,
    "lyap_inner_prod_coords": lyap_coords,   # list of N+1 matrices (nested lists)
    "grouping_code": grouping_code,           # Python source to reconstruct lyap
    "extra_duals": extra_duals,               # dict of name -> float
}
with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json", "w") as fh:
    json.dump(state, fh, indent=2)
print("State saved to examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json")
print("Rank profile:", ranks)
EOF
```

---

## Step 8 — Update Lyapunov Notebook

Open the existing notebook and add or replace the Lyapunov partial-sum section, following the `Identify the vectors composing the Lyapunov function` lead-in from `examples_peppy/_references/gd/gd_example_lyap.ipynb`.

The notebook cells for this block must show:
- extraction of interpolation duals and extra constraint duals
- LDL/direct S ingredients used in the partial sums
- the actual `lyap = [...]`, `partial_sum = ...`, and update loop; do not hide this behind `exec(grouping_code)`
- rank profile computation inside the visible partial-sum construction cell
- coverage check for `lyap[N]`

Make the first Block 3 notebook cell human-interpretable. It should summarize the partial-sum increments in rendered LaTeX, for example `$$V_{k+1} - V_k = c_1\operatorname{Lip}(x_{k+1/2}, x_{k+1}) + c_2\operatorname{Mon}(x_k, x_{k+1})$$`, and explain the rank profile and coverage residual in words. Do not print these equations as monospace text output when they can be displayed as Markdown/LaTeX. Do not expose raw JSON dictionaries such as `grouping_terms` as the primary notebook output; raw state dumps may be kept only as optional debug details.

In the visible partial-sum construction cell, print the rank of each constructed Lyapunov term immediately after building `lyap`, one line per term. Print a blank line after `rank V_0: ...`, then print the interior-rank consistency check in the same cell:

```python
ranks = []
for k, Vk in enumerate(lyap):
    matrix = pm.eval_scalar(Vk).inner_prod_coords.astype(float)
    rank = int(np.linalg.matrix_rank(matrix, tol=rank_tolerance))
    ranks.append(rank)
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()

print("Interior rank is constant:", len(set(ranks[1:N_int])) == 1)
```

Do not create a separate `### Rank Profile` cell just to print the stored and computed rank lists or coefficient matrices. Do not print the grouped dual terms by default, e.g. avoid output like `V_k terms:` followed by every `(kind, ri, ci, coeff)` entry. The construction code should remain visible, but its primary output should be the rank profile in the line-by-line format above and the single interior-rank consistency line.

If producing that readable summary requires nontrivial formatting helpers, move those helpers into `examples_peppy/{ALGO_NAME}/notebook_helpers.py` or another small local module and call them from the notebook. The notebook should show the summary output and a simple helper call, not long helper definitions such as fraction formatters, tag renderers, or residual-name pretty-printers. Do not hide the actual partial-sum construction, rank computation, or coverage check in this helper; those remain visible notebook workflow code.

Keep these cells executable with the state files under `examples_peppy/{ALGO_NAME}/state/`.

---

## Output

Report:
- The rank profile `[r_0, r_1, ..., r_N]` — confirm it is constant across k=1..N−1
- Which dual terms are grouped at each step
- Whether `lyap[N]` has near-zero rank (boundary coverage)

- Confirmation that the notebook was updated through the partial-sum/rank-profile section

**Next step**: `/lyap-vectors {ALGO_NAME}`
