# /lyap-closed-form: PEPFlow Block 5 — Find Closed-Form Lyapunov Function

Using the Lyapunov structure from Block 4 and the closed-form dual certificates from Block 2, build and solve the symbolic recursion V_{k+1} − V_k = dual contributions, verify three symbolic identities, and produce a human-readable proof.

> $ARGUMENTS  (ALGO_NAME, e.g. `heavy_ball`)

---

## Environment

PEPFlow repo root: `$(git rev-parse --show-toplevel)/`
Python executable: `.venv/bin/python3`
Input: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json`
Output: `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` + printed LaTeX proof
Notebook: finalize the existing notebook created by Block 1

---

## Reference Scope

When looking for reference examples, notebook structure, proof-writing patterns, or prompt skeletons, use only files under `examples_peppy/`. The `examples_peppy/_references/` subtree is explicitly allowed and may be used freely as reference material. Do not inspect or follow other repository example/reference files outside `examples_peppy/` for this workflow.

---

## Step 1 — Load State

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import json
b4 = json.load(open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json"))
print("algo_name:", b4["algo_name"])
print("basis_templates:", b4.get("basis_templates", []))
print("coeff_by_k keys:", list(b4["coeff_by_k"].keys()))
print("rank_profile:", b4["rank_profile"])
EOF
```

Extract: `ALGO_NAME`, `basis_templates`, `coeff_code`, `lamb_code`, `S_code`, `S_decomp_type`.

---

## Step 2 — Set Up Symbolic Recursion Context

Create a minimal one-step PEPFlow context with symbolic parameters `k` and `N`:

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import pepflow as pf, numpy as np, sympy as sp, json, importlib.util

b4 = json.load(open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json"))

# Symbolic parameters for the recursion
k_sym = pf.Parameter("k")
N_sym = pf.Parameter("N")
k_sp  = sp.Symbol("k", positive=True)
N_sp  = sp.Symbol("N", positive=True)

# Algorithm-specific parameters (from b4["params_json"])
params_literal = json.loads(b4["params_json"])
params_symbolic = {}
for pname, pval in params_literal.items():
    if pname in ("R",):
        continue  # R is only in initial condition
    params_symbolic[pname] = sp.Symbol(pname, positive=True)

# Create a one-step context encoding x_k -> x_{k+1} -> x_{k+2}
# (Use algorithm-specific basis: abstract vectors for x_k, x_{k+1}, plus
#  any operator outputs or gradients needed by V_k and V_{k+1})
ctx_lyap = pf.PEPContext("lyap_recursion").set_as_current()

# Define abstract basis vectors for a generic step:
# - For smooth function problems (GD-like), basis is {grad_f(x_k), grad_f(x_{k+1}), x_0 - x_star}
# - For operator problems (APPM-like), basis is {A(x_k), A(x_{k+1}), x_0 - x_k}
# Adapt this to the algorithm; use pf.Vector(is_basis=True, tags=[...]) for each.

# Example (smooth function, 2 consecutive iterates needed):
xk   = pf.Vector(is_basis=True, tags=["x_k"])
xk1  = pf.Vector(is_basis=True, tags=["x_{k+1}"])
# grad or operator outputs as additional basis vectors:
# gk  = pf.Vector(is_basis=True, tags=["grad_f(x_k)"])
# gk1 = pf.Vector(is_basis=True, tags=["grad_f(x_{k+1})"])

# Express V_k and V_{k+1} symbolically using the basis and coeff_pattern from Block 4.
# The coefficient functions a(k,N), b(k,N), ... are filled in from the pattern identified.
# Example (2-vector basis V_k = a*xk^2 + b*xk*(xk1-xk) + c*(xk1-xk)^2):
a_k  = sp.Function("a")(k_sp, N_sp)   # replace with the actual closed-form expression
# V_k   = a_k * xk**2 + ...
# V_k1  = a_k.subs(k_sp, k_sp+1) * xk1**2 + ...

print("Context ready. Define V_k, V_{k+1} symbolically before Step 3.")
EOF
```

**Nontrivial checkpoint**: The structure of `ctx_lyap` depends heavily on the algorithm. If the algorithm has more than 2 iterates in the V_k expression (e.g., V_k involves x_{k-1} as well), define additional basis vectors. If the coefficient pattern from Block 4 is unclear, revisit `/lyap-vectors` before continuing.

---

## Step 3 — Symbolic Recursion: Step Identity

Build the expression `V_{k+1} − V_k − Σ(dual_k * ineq_k) - (S contribution)` and verify it is identically zero:

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
# (continuing — ctx_lyap, V_k, V_k1, params_symbolic, k_sp, N_sp defined)

pm_lyap = pf.ExpressionManager(ctx_lyap,
    resolve_parameters={**params_symbolic, "k": k_sp, "N": N_sp})

# Single-step dual contribution: λ_k * interp(x_k, x_{k+1})
# (plus any extra dual terms — Lipschitz etc. — at this step)
# Fill in using the closed-form lamb() from b4["lamb_code"]:
exec(b4["lamb_code"].replace("N_int", "N_sp").replace("N=N_int", "N=N_sp"))
# lam_k = lamb(f"x_k", f"x_{{k+1}}", N=N_sp)  # adjust tag names

# Step contribution (adapt to problem type):
# step_contrib = lam_k * interp_expr + ...  # define interp manually for ctx_lyap

# diff_step = V_k1 - V_k - step_contrib
# mat = pm_lyap.eval_scalar(diff_step).inner_prod_coords
# mat_simp = sp.Matrix([[sp.simplify(e) for e in row] for row in mat])
# print("Step identity zero:", mat_simp == sp.zeros(*mat_simp.shape))
# pf.pprint_str(diff_step.repr_by_basis(ctx_lyap, sympy_mode=True,
#               resolve_parameters={**params_symbolic, "k": k_sp, "N": N_sp}))
EOF
```

If `mat_simp` is not identically zero, use `sympy.simplify` on each entry and print the residual to locate which coefficient is wrong. Adjust the coefficient formula `a(k,N)`, `b(k,N)`, etc. and re-run.

---

## Step 4 — Base Case (k=0 or k=1)

Verify `V_1 − V_0 = (terms from the very first step)`:

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import sympy as sp
# Create a separate minimal context for k=0 -> k=1.
# Substitute k=0 (or k=1) into the step recursion and check
# whether the missing "initial" terms account for the difference.

# Base case: diff_base = V_1 - V_0 - base_contribution
# base_contribution may include: initial interp terms, first Lipschitz term, etc.
# mat_base = pm_base.eval_scalar(diff_base).inner_prod_coords
# mat_base_simp = sp.Matrix([[sp.simplify(e) for e in row] for row in mat_base])
# print("Base case zero:", mat_base_simp == sp.zeros(*mat_base_simp.shape))
EOF
```

---

## Step 5 — Boundary Identity (Final Step)

Verify the telescoping identity that connects V_N to the performance bound:
`τ * IC − perf − S_guess + V_N + λ_N * interp(x_N, x_star) = 0`

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import pepflow as pf, numpy as np, sympy as sp, importlib.util, json

b4 = json.load(open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json"))
N_sym = sp.Symbol("N", positive=True)

# Load the original setup and solve with symbolic N (use a concrete N for verification):
N_concrete = sp.S(b4["N_verify"])
params_sp = {k: sp.Rational(str(v)) if isinstance(v, (int, float)) else sp.S(v)
             for k, v in json.loads(b4["params_json"]).items()}

spec = importlib.util.spec_from_file_location("setup",
    "examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
ctx, pb, obj = mod.get_pep_setup(N_concrete, params_sp)
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)

N_int = int(N_concrete)
x_N, x_0, x_star = ctx[f"x_{N_int}"], ctx["x_0"], ctx["x_star"]
tau = sp.S(b4["tau_sol"])
R = pf.Parameter("R")

# V_N evaluated numerically (use coefficient formula at k=N):
# V_N_expr = coeff_pattern(N_int, N_int)(0,0) * ... (paste from coeff_code)

# boundary_lhs = tau * (x_0 - x_star)**2 - (obj(x_N) - obj(x_star)) - S_guess + V_N_expr
#                + lamb("x_star", f"x_{N_int}") * obj.interp_ineq("x_star", f"x_{N_int}")
# mat = pm.eval_scalar(boundary_lhs).inner_prod_coords
# print("Boundary identity zero:", np.allclose(mat, 0, atol=1e-6))
EOF
```

**Nontrivial checkpoint**: If the boundary identity does not cancel, check that `V_N` evaluated at `k=N` uses the correct coefficient formula (some coefficient patterns have a special form at k=N). Print the residual matrix and ask the user if needed.

---

## Step 6 — Assemble Human-Readable Proof

Once all three identities are verified, write the proof in a structured form:

```
Theorem: For the {ALGO_NAME} algorithm on {PROBLEM_TYPE} functions with {INITIAL_CONDITION},
         after N iterations: {PERFORMANCE_METRIC} ≤ {CONJECTURED_RATE}.

Proof:
Define V_k = (full closed-form expression in terms of special vectors with closed-form coefficients).
The proof outline must display this formula explicitly in LaTeX, including the valid
index range and any coefficient definitions such as a_k, theta_k, or beta_k.

1. (Base case) V_1 − V_0 = (base contribution) ≤ 0 because ...

2. (Step recursion, k=1..N-1) V_{k+1} − V_k = λ_k * interp(x_k, x_{k+1}) + ... ≤ 0
   since interpolation inequalities are ≤ 0 and all duals λ_k ≥ 0.
   Therefore V_k is nonincreasing: V_N ≤ ... ≤ V_1 ≤ 0.
   This must be written as a detailed equation, not as an ellipsis-only summary:
   include every active interpolation residual family, every extra constraint
   residual, and every negative slack/square term that appears in the per-step
   certificate. Define the residual notation used in the equation (for example
   I_f(u,v), I_g(u,v), Lipschitz residuals, monotonicity residuals, and S_k).

3. (Boundary) {CONJECTURED_RATE} * ||x_0 - x_star||^2 ≥ perf_metric + S_guess − V_N
              − λ_N * interp(x_N, x_star) ≥ perf_metric.
   Hence {PERFORMANCE_METRIC} ≤ {CONJECTURED_RATE}. □
```

Print the proof in both symbolic and LaTeX forms.

---

## Step 7 — Finalize Lyapunov Notebook

The notebook is the primary deliverable of this block. It must reproduce the workflow, not merely summarize the final theorem.

Update the existing `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` created in Block 1. Do not replace it with a compact final notebook; preserve and refine the diagnostic sections added by Blocks 1-4.

Follow the structure of the most relevant reference:
- `examples_peppy/_references/gd/gd_example_lyap.ipynb` for smooth convex problems
- `examples_peppy/_references/appm/appm_example_lyap.ipynb` for monotone operator problems

The notebook must include (in this order):
1. Title and algorithm description
2. **Proof statement cells**: an unnumbered heading-only `## Proof Statement` cell, followed by a `### Theorem` cell and a separate `### Proof outline` cell with formatted LaTeX. The theorem cell must be self-contained and include, at minimum:
   - the assumptions, algorithm recurrence, and convergence guarantee
   - the full closed-form Lyapunov function `V_k`, including its valid index range and any terminal/special-case formula
   - every function-value term in `V_k` when `func_coords` are nonzero, with exact coefficients

   The proof outline must then repeat the proof-critical parts of the Lyapunov function as needed and include, at minimum:
   - definitions of the interpolation/constraint residuals used in the proof
   - the detailed per-step increment identity for `V_{k+1}-V_k` or `V_k-V_{k-1}` with all active residual terms and slack/square terms shown explicitly
   - the boundary identity explaining which terminal terms remain after the partial sums
3. Imports: `pepflow`, `numpy`, `sympy`, `matplotlib`, `itertools`, `pepflow.lyapunov_utils`
4. Context creation (`make_ctx_{ALGO_NAME}`)
5. Dense + relaxed solve (from Block 2 results), displaying certificate matrices with `pf.pprint_labeled_matrix` using their row and column labels
6. S decomposition (LDL or direct, from Block 2), showing the true S certificate matrix with `pf.pprint_labeled_matrix`, the stored guessed S formula with `pf.pprint_str(b5['S_formula'])`, and the matrix match check
7. Partial sum construction with rank profile (from Block 3), with the `lyap`/partial-sum definition written explicitly in the notebook cell
8. Candidate vector generation and column-space filtering (from Block 4)
9. Coefficient matrix extraction per k with fractions (from Block 4), displaying coefficient matrices with `pf.pprint_labeled_matrix`
10. Symbolic step recursion check (from Step 3 of this block), built with PEPFlow contexts, Scalars, and `pf.ExpressionManager`
11. Base case and boundary symbolic verification (Steps 4–5), built with PEPFlow contexts, Scalars, and `pf.ExpressionManager`, with base and boundary in separate markdown/code cells

The first code cell should keep ordinary imports at the top, then insert the repository root into `sys.path`, then import repo-local modules such as `pepflow` with an explicit `# noqa: E402`. This lets notebook execution use the repo-local package rather than a stale installed package while keeping Ruff's import-order rule intentional. Use paths anchored at the repository root inside the notebook so it executes correctly even when the kernel starts in `examples_peppy/{ALGO_NAME}`.

Write notebook code so it is friendly to static checks (`ruff` and `ty`) even when the notebook uses dynamic workflow artifacts. If a cell uses `exec(...)` to load generated helper functions, bind the expected names explicitly from `globals()` with type annotations immediately afterward, for example `V_k_basis: Callable[[int], list[Any]] = globals()["V_k_basis"]`. Guard dynamic imports from `importlib.util.spec_from_file_location(...)` with `if spec is None or spec.loader is None: raise ImportError(...)` before calling `exec_module`. Avoid bare `display(...)` calls unless `display` is imported explicitly, and simplify SymPy matrices elementwise with `sp.Matrix(...).applyfunc(sp.simplify)` rather than `sp.simplify(sp.Matrix(...))`.

Keep supporting Python modules friendly to `ty` as well. For functions that return structured JSON containing nested dictionaries, lists, and scalar values, annotate the output shape broadly enough, such as `dict[str, Any]`, or define a precise `TypedDict`; do not let `ty` infer a too-narrow union from the first few keys before later assigning nested entries like `lambda_groups`. For optional integration imports that may be absent from the local type-check environment, prefer installing the declared dependency; if the dependency is intentionally optional, use a narrow `# ty: ignore[unresolved-import]` on that import only, and keep any `# noqa: E402` import-order suppression separate and explicit.

When displaying dense or relaxed certificate matrices in the notebook, use `pf.pprint_labeled_matrix(...)` with the stored row and column names. For multiple lambda groups, display each group as a labeled matrix before printing any optional nonzero-entry fraction summary. Avoid replacing the labeled matrix display with manual nested-loop text dumps.

For the S decomposition/direct S formula cell, keep the output focused: display the true S matrix from the certificate with `pf.pprint_labeled_matrix(...)`, display the stored guessed S formula with `pf.pprint_str(b5['S_formula'])`, and print the numerical matrix comparison such as `S matches relaxed matrix: True`. Avoid dumping both the guessed matrix and true matrix unless the comparison fails.

For the partial-sum/rank-profile cell, write out the actual `lyap = [...]`, `partial_sum = ...`, and update loop that defines the Lyapunov partial sums. Do not hide this definition behind `exec(b5['grouping_code'])` or another serialized-code shortcut; the notebook must show the mathematical construction before printing the rank profile.

For the coefficient extraction cell, use `pf.pprint_labeled_matrix(...)` to display coefficient matrices with the active basis-vector labels. When comparing decomposed coefficients against closed-form formulas, show both the decomposed matrix and the closed-form matrix as labeled matrices before printing the match check. Avoid raw `print(C)` or unlabeled NumPy matrix dumps for these outputs.

Immediately after coefficient extraction and before symbolic step recursion verification, add a markdown conclusion stating the resulting closed-form Lyapunov function `V_k` in LaTeX. This cell should summarize the coefficient pattern found by the extraction and explicitly say that the next section symbolically verifies the one-step recursion for this `V_k`.

The `### Theorem` cell near the top of the notebook must explicitly state the final closed-form `V_k` formula, not merely the convergence rate. The `### Proof outline` cell must be mathematically self-contained enough that a reader can follow the proof without reading the code cells first. At a minimum, it must repeat the proof-critical parts of the final `V_k` formula and spell out the detailed `V_{k+1}-V_k` (or shifted `V_k-V_{k-1}`) identity, including all interpolation residuals, extra residuals, and slack/square terms. Do not replace these with phrases like "dual contributions", "certificate terms", or an ellipsis.

When the evaluated Lyapunov partial sums have nonzero function coordinates (`func_coords`), the closed-form `V_k` must include the corresponding function-value gap terms, such as `f(x_k)-f(x_star)` or `(f+g)(x_k)-(f+g)(x_star)`, with their exact coefficients. Do not present only the quadratic/inner-product part from `inner_prod_coords`; compare and report both the function-coordinate pattern and the inner-product coefficient matrix.

For symbolic step, base, and boundary identity cells, follow the package-native style used in `examples_peppy/_references/gd/gd_example_lyap.ipynb` and the relevant `examples_peppy/_references/.../*_example_lyap.ipynb` notebook: create an auxiliary `pf.PEPContext`, define symbolic parameters such as `k`, `N`, and algorithm parameters with `pf.Parameter`/SymPy symbols, define the symbolic iterates with PEPFlow `Vector`, `Parameter`, operator/function calls, form `LHS`, `RHS`, and `diff` as PEPFlow `Scalar` expressions, and use `pf.ExpressionManager` to extract and simplify the residual coordinates. Display residual matrices with `pf.pprint_labeled_matrix(...)`.

The symbolic verification cells must contain the actual symbolic calculation code in the notebook itself. They must not merely assert stored booleans from `b5`, call a helper such as `_closed_form_verify.py`, or replay a concrete-N verification from earlier blocks. Helper scripts may supplement the notebook, but each symbolic verification cell must visibly construct the symbolic context, the symbolic identity, and the simplified residual. For function-valued Lyapunov expressions, the cell must also extract and simplify `func_coords` and show that those residuals are zero, not only `inner_prod_coords`.

Immediately after every symbolic verification heading, add a markdown cell with the exact LaTeX equation being verified before the code cell. This applies at least to `## Symbolic Step Recursion Verification`, `## Base Case and Boundary Symbolic Verification`, and `### Boundary Identity Symbolic Verification`. The equation cell should state the identity and say that the residual `$\mathrm{LHS}-\mathrm{RHS}$` should simplify to zero.

Keep the base case and boundary identity symbolic verifications in separate notebook cells, with a clear markdown heading before the boundary cell such as `### Boundary Identity Symbolic Verification`. Do not combine the base residual calculation and the boundary residual calculation in one long code cell.

For auxiliary symbolic contexts, distinguish Python variable names from rendered PEPFlow tags. Python identifiers may use snake case such as `A_step`, `A_base`, or `A_boundary`, but the rendered tags passed to PEPFlow objects should use clear math notation with braces, such as `tags=['A_{step}']`, `tags=['A_{base}']`, and `tags=['A_{boundary}']`. This avoids tag collisions with the main operator and prevents ambiguous notebook labels like `A_step(x_k)`.

For markdown proof cells, use notebook-compatible math delimiters: `$...$` for inline math and `$$...$$` for display math. Do not rely on `\(...\)` or `\[...\]`, because some notebook frontends render those as plain text. After notebook execution, inspect the proof statement cell source and rendered output for raw TeX delimiters or missing equation operators.

When generating markdown cells programmatically, protect LaTeX backslashes from Python escape sequences. Use raw strings or doubled backslashes for commands such as `\frac`, `\right`, `\le`, and `\operatorname`. Before reporting completion, scan the notebook source for control characters such as form-feed (`\f`) or carriage-return (`\r`) inside markdown cells; these usually indicate an escaped LaTeX command was corrupted and will cause KaTeX parse errors.

In markdown and displayed formulas, always brace subscripts and superscripts that are not single literal symbols: write `x_{0}`, `x_{k+1}`, `x_{k+1/2}`, `A_{k}`, and `V_{N}` rather than `x_0`, `x_k+1`, or `V_N`. This prevents notebook LaTeX parsing ambiguity and keeps rendered mathematical notation consistent.

Place the proof statement section immediately after the title/algorithm description and before the imports. Keep the proof section structurally clear: do not combine the theorem statement and proof into one large markdown cell. Use one unnumbered heading-only cell for `## Proof Statement`, never `## 10. Proof Statement`, one cell titled `### Theorem`, and one cell titled `### Proof outline`.

The `### Theorem` cell must not be only a rate statement. It must present the Lyapunov certificate `V_k` before or alongside the claimed guarantee, so a reader sees the theorem and certificate without having to search later diagnostic sections.

Do not add a final numerical/symbolic verification section if it only repeats the already verified boundary identity in the recreated concrete context. The boundary identity symbolic verification is the authoritative final identity verification; an extra `## Numerical Verification of Final Identity` section is optional only when it verifies a genuinely different end-to-end condition.

After writing the notebook, execute it end to end before reporting completion:

```bash
mkdir -p examples_peppy/{ALGO_NAME}/state/.runtime
export JUPYTER_RUNTIME_DIR="$(pwd)/examples_peppy/{ALGO_NAME}/state/.runtime"
export TMPDIR="$(pwd)/examples_peppy/{ALGO_NAME}/state/.runtime"
.venv/Scripts/python.exe -m jupyter nbconvert \
  --to notebook \
  --execute examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb \
  --output {ALGO_NAME}_example_lyap.ipynb \
  --output-dir examples_peppy/{ALGO_NAME}
```

On Windows PowerShell, set the same runtime directories before executing:

```powershell
New-Item -ItemType Directory -Force examples_peppy/{ALGO_NAME}/state/.runtime | Out-Null
$runtime = (Resolve-Path examples_peppy/{ALGO_NAME}/state/.runtime).Path
$env:JUPYTER_RUNTIME_DIR = $runtime
$env:TMPDIR = $runtime
$env:TMP = $runtime
$env:TEMP = $runtime
.venv\Scripts\python.exe -m jupyter nbconvert `
  --to notebook `
  --execute examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb `
  --output {ALGO_NAME}_example_lyap.ipynb `
  --output-dir examples_peppy/{ALGO_NAME}
```

The `.runtime/` directory is only for Jupyter/Python tool files such as kernel connection files. It is not part of the workflow state contract; do not store certificates, basis data, dual values, closed-form guesses, or other meaningful workflow artifacts there. Those durable artifacts stay under `examples_peppy/{ALGO_NAME}/state/`.

If notebook execution fails, fix the notebook and rerun it. Do not report completion based only on a standalone script or a compact proof-only notebook.

After execution, run static checks on the generated notebook and fix issues in the notebook source:

```bash
ruff check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb
uvx ty check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb
```

If `uv` is not available in the environment, use an installed `ty` executable instead:

```bash
ty check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb
```

Treat `uvx ty check ...` as the preferred self-contained command and `ty check ...` as the fallback for pip/conda environments where `ty` has already been installed.

After the notebook executes, confirm its path and print the final Lyapunov function and convergence theorem in mathematical notation.

---

## Definition of Done

This block is not complete until all of the following are true:

1. `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` contains separate cells for every Step 1-7 section in this workflow.
2. The notebook is not a compact proof-only artifact. It must include the diagnostic trail:
   - state loading
   - symbolic recursion context
   - dense/relaxed certificate inspection with labeled matrix displays via `pf.pprint_labeled_matrix`
   - S decomposition or direct S formula verification with a labeled true S matrix, `pf.pprint_str(b5['S_formula'])`, and a matrix match check
   - explicit partial sum reconstruction defining `lyap` and `partial_sum` in the notebook cell
   - rank profile
   - special vector/basis reconstruction from Block 4
   - coefficient extraction and formula verification with labeled decomposed and closed-form coefficient matrices
   - markdown conclusion after coefficient extraction stating the closed-form Lyapunov function `V_k`
   - if `func_coords` are nonzero, the closed-form `V_k` includes all function-value gap terms with exact coefficients
   - theorem markdown near the top that explicitly states the final closed-form Lyapunov function `V_k`, including terminal/special cases
   - proof outline markdown near the top that explicitly states the final `V_k` formula
   - proof outline markdown near the top that explicitly states the detailed `V_{k+1}-V_k` or `V_k-V_{k-1}` equation with all residual and slack terms
   - symbolic step identity implemented in the notebook cell itself with symbolic PEPFlow expressions and `pf.ExpressionManager`; no stored-boolean-only checks
   - base identity implemented in the notebook cell itself with symbolic PEPFlow expressions and `pf.ExpressionManager`; no stored-boolean-only checks
   - boundary identity implemented in the notebook cell itself with symbolic PEPFlow expressions and `pf.ExpressionManager`; no stored-boolean-only checks
   - if the Lyapunov expression contains function values, symbolic verification cells display and check both `inner_prod_coords` and `func_coords`
   - markdown equation cells immediately after each check heading stating the identity being verified
   - separate proof statement cells: unnumbered `## Proof Statement`, `### Theorem`, and `### Proof outline`
   - rendered proof cells with no raw TeX delimiters shown as text
3. All three identities must be verified by executable symbolic code in the notebook:
   - step identity residual is exactly zero or simplifies to zero through `pf.ExpressionManager` coordinates using symbolic `k`, `N`, and algorithm parameters where applicable
   - base identity residual is exactly zero or simplifies to zero through `pf.ExpressionManager` coordinates using symbolic `N` and algorithm parameters where applicable
   - boundary identity residual is exactly zero or simplifies to zero through `pf.ExpressionManager` coordinates using symbolic `N` and algorithm parameters where applicable
   - the code cells visibly build `LHS`, `RHS`, and `diff`; a call to a helper script or an assertion of a stored state flag does not satisfy this requirement
4. The notebook must be executed with `jupyter nbconvert --execute` before the block is reported complete.
5. `ruff check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` must pass for this generated notebook. The type check must also pass, using either `uvx ty check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` if `uv` is available, or `ty check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` otherwise.
6. If notebook execution or static checks fail, fix the notebook and rerun the failing command.
7. Store any helper verification script in `examples_peppy/{ALGO_NAME}/state/` only if the notebook calls or references it.
8. Save durable Block 5 state to `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b5.json`.

---

## Output

Report:
- The closed-form Lyapunov function `V_k` in mathematical notation
- Confirmation that all three symbolic identities (step, base, boundary) are zero
- Path to the generated notebook `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb`
- The LaTeX theorem statement

This completes the 5-block PEPFlow workflow: algorithm definition → numerical proof → Lyapunov function → human-verifiable convergence theorem.
