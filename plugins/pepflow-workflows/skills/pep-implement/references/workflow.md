# /pep-implement: PEPFlow Block 1 — Algorithm Implementation

Parse an algorithm description, create a PEPFlow setup module, and obtain numerical convergence rates.

> $ARGUMENTS

---

## Environment

PEPFlow repo root: `$(git rev-parse --show-toplevel)/`
Python executable: `.venv/bin/python3` (use this for ALL Python calls)
State output: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json`
Notebook output: `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb`

---

## Notebook Lifecycle

Start the Lyapunov notebook in Block 1 and keep updating the same file in every later block. Do not wait until `/lyap-closed-form` to create it.

Use `examples_peppy/_references/gd/gd_example_lyap.ipynb` as the structural reference. The notebook should grow in this order:
1. title, problem description, and the algorithm update equations in LaTeX
2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5
3. imports
4. function/operator definitions
5. `make_ctx_{ALGO_NAME}` and `get_pep_setup`
6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate
7. dense and relaxed proof solves
8. closed-form lambda and S verification
9. partial-sum Lyapunov construction and rank profile
10. special-vector identification
11. coefficient extraction and closed-form `V_k`
12. symbolic step, base, and boundary identities

Each block owns the cells matching the work it just completed. Prefer updating or replacing that block's section in the existing notebook over rebuilding the notebook from scratch, so the notebook remains a readable record of the workflow.

Keep notebook cells focused on the mathematical workflow and the human decisions being made. Expose algorithm definitions, partial-sum constructions, candidate bases, coefficient extraction, and symbolic verification code when those are part of the proof reasoning. Move presentation-only helpers, repetitive formatting functions, and raw state pretty-printers into a small local helper module such as `examples_peppy/{ALGO_NAME}/notebook_helpers.py`, then call that helper from the notebook. Helper modules may format tables or summaries, but they must not hide proof-critical construction or verification logic.

When writing notebook markdown from Python strings, use raw strings or escaped backslashes for LaTeX commands. In particular, write `r"\frac{...}{...}"` or `"\\frac{...}{...}"`; never let `\frac`, `\right`, or similar commands pass through ordinary Python string escapes where `\f` or `\r` can become control characters.

When executing notebooks, avoid relying on system-level temporary directories such as `/tmp`, `C:\tmp`, or vendor-specific temp folders. If needed, configure Jupyter/Python runtime directories to use a repository-local scratch directory, for example `examples_peppy/{ALGO_NAME}/state/.runtime/`. This directory is only for tool/runtime files such as Jupyter kernel connection files. It is not part of the workflow state contract and should not be used to store certificates, basis data, dual values, or other meaningful intermediate artifacts. Workflow-level artifacts remain under `examples_peppy/{ALGO_NAME}/state/`.

---

## Reference Scope

When looking for reference examples, notebook structure, proof-writing patterns, or prompt skeletons, use only files under `examples_peppy/`. The `examples_peppy/_references/` subtree is explicitly allowed and may be used freely as reference material. Do not inspect or follow other repository example/reference files outside `examples_peppy/` for this workflow.

---

## Step 1 — Parse

From `$ARGUMENTS`, identify:

| Field | Description |
|---|---|
| `ALGO_NAME` | `snake_case` identifier, e.g. `heavy_ball` |
| `PROBLEM_TYPE` | `smooth_convex` / `smooth_strongly_convex` / `monotone_operator` / `composite` |
| `OBJ_TAG` | `"f"` (functions) or `"A"` (operators) |
| `PARAMS` | All symbolic parameters (e.g. `L`, `alpha`, `beta`, `R`) |
| `PERFORMANCE_METRIC` | e.g. `f(x_N) - f(x_star)` or `‖A(x_N)‖²` |
| `INITIAL_CONDITION` | e.g. `‖x_0 - x_star‖² ≤ R²` |
| `CONJECTURED_RATE` | Known bound or `"unknown"` |

Print a brief summary of what you identified, then proceed.

---

## Step 2 — Create Setup Module

**If** `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py` already exists, read it and confirm correctness. Skip creation if valid.

Otherwise read the reference notebook for your problem type, e.g.:
- `smooth_convex` / `smooth_strongly_convex` → `examples_peppy/_references/gd/gd_example.ipynb`
- `monotone_operator` → `examples_peppy/_references/appm/appm_example.ipynb`
- `composite` → `examples_peppy/_references/pgm/pgm_example.ipynb`

Create `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py` following this structure:

```python
"""
{ALGO_NAME} setup module for pep_runner.py.

Algorithm: (one-line description)
Performance metric: (e.g., f(x_N) - f(x_star))
Initial condition: (e.g., ‖x_0 - x_star‖² ≤ R²)
Conjectured rate: (to be determined)
"""
import pepflow as pf
import sympy as sp

# Module-level objects — shared across get_pep_setup calls
L = pf.Parameter("L")
f = pf.SmoothConvexFunction(is_basis=True, tags=["f"], L=L)
# For operators: A = pf.MonotoneOperator(is_basis=True, tags=["A"])


def make_ctx_{ALGO_NAME}(ctx_name: str, N, **kwargs) -> pf.PEPContext:
    """Build the PEPContext encoding N steps of the algorithm."""
    ctx = pf.PEPContext(ctx_name).set_as_current()
    x = pf.Vector(is_basis=True, tags=["x_0"])
    f.set_stationary_point("x_star")  # or A.set_zero_point("x_star")

    for i in range(N):
        # TODO: replace with actual update rule
        x = x - 1 / L * f.grad(x)
        x.add_tag(f"x_{i + 1}")

    return ctx


def get_pep_setup(N, params):
    """Standard interface for pep_runner.py."""
    R = pf.Parameter("R")
    ctx = make_ctx_{ALGO_NAME}(f"ctx_{N}", N)
    pb = pf.PEPBuilder(ctx)
    pb.add_initial_constraint(
        ((ctx["x_0"] - ctx["x_star"]) ** 2).le(R, name="initial_condition")
    )
    pb.set_performance_metric(f(ctx[f"x_{N}"]) - f(ctx["x_star"]))
    return ctx, pb, f
```

**Nontrivial checkpoint**: If the update rule involves operators or patterns not covered by the PEPFlow API (see CLAUDE.md), stop and ask the user for guidance before creating the file.

---

## Step 3 — Numerical Sweep

Run the sweep for N = 1..7:

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 -m pepflow.pep_runner \
    --module examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py \
    --sweep 1:8 \
    --params '{"L": 1, "R": 1}' \
| .venv/bin/python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data['results']:
    print(f'N={r[\"N\"]}: {r[\"opt_value\"]:.8f}')
"
```

If the sweep fails, diagnose and fix the setup module (check the algorithm update rule, tags, and performance metric) before continuing.

---

## Step 4 — Identify Rate

Detect the convergence rate pattern:

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 -m pepflow.pep_runner \
    --module examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py \
    --sweep 1:8 \
    --params '{"L": 1, "R": 1}' \
| .venv/bin/python3 - <<'PYEOF'
import sys, json, fractions
data = json.load(sys.stdin)
opts = [r["opt_value"] for r in data["results"]]
# Save sweep data for state file
import os; os.makedirs("examples_peppy/{ALGO_NAME}/state", exist_ok=True)
with open("examples_peppy/{ALGO_NAME}/state/_sweep_tmp.json", "w") as fh:
    json.dump(data["results"], fh)

inv_opts = [1/v for v in opts if v > 1e-10]
diffs    = [inv_opts[i+1] - inv_opts[i] for i in range(len(inv_opts)-1)]
print("opt_values:  ", [round(v,6) for v in opts])
print("1/opt:       ", [round(v,3) for v in inv_opts])
print("Δ(1/opt):    ", [round(d,3) for d in diffs])
print("Exact fractions of opt_values:")
for i, v in enumerate(opts):
    print(f"  N={i+1}: {fractions.Fraction(v).limit_denominator(1000)}")
PYEOF
```

Interpret:
- Constant Δ(1/opt) → rate ~ C/N
- Linearly growing Δ(1/opt) → rate ~ C/N²
- Geometric Δ(1/opt) → exponential convergence

If you cannot easily infer the rate formula from the numerics, consider sweeping larger values of N (up to 15--20).

If `CONJECTURED_RATE` was given, verify it matches.

---

## Step 5 — Save State

Save all extracted information to `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json`. Replace placeholders with actual values identified:

```python
import json, os
os.makedirs("examples_peppy/{ALGO_NAME}/state", exist_ok=True)
results = json.load(open("examples_peppy/{ALGO_NAME}/state/_sweep_tmp.json"))
state = {
    "algo_name": "{ALGO_NAME}",
    "problem_type": "{PROBLEM_TYPE}",
    "obj_tag": "{OBJ_TAG}",
    "params_json": '{"L": 1, "R": 1}',          # extend with algorithm-specific params
    "performance_metric": "{PERFORMANCE_METRIC}",
    "initial_condition": "{INITIAL_CONDITION}",
    "conjectured_rate": "{DISCOVERED_RATE}",      # formula as string, or "unknown"
    "setup_file": "examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py",
    "sweep_results": results,
    "N_verify": 4,                                 # default; increase to 6 for complex algorithms
}
with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json", "w") as fh:
    json.dump(state, fh, indent=2)
print("State saved to examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json")
```

---

## Step 6 — Initialize Lyapunov Notebook

Create `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` now. It should be executable, even though later proof sections are still placeholders.

Following the early structure of `examples_peppy/_references/gd/gd_example_lyap.ipynb`, include:
- title, one-paragraph problem description, and the algorithm update equations in LaTeX
- imports cell, using the repo-local import pattern expected for notebooks
- function/operator and parameter definitions
- the actual algorithm/PEP setup code, including parameters, iterate tags, update rule, initial condition, and performance metric
- numerical evidence cell using the Block 1 sweep results, including both printed values and a matplotlib plot of PEP values versus the discovered or conjectured rate curve
- a short markdown cell listing the conjectured rate and saying later sections will fill in the proof certificate, Lyapunov construction, and symbolic identities

The first notebook cell should let a reader understand the problem and algorithm without reading code: include the main assumptions, performance metric, and displayed LaTeX equations for the iterate updates. The notebook should also expose the algorithm definition as readable, executable notebook code. Do expose the context builder and `get_pep_setup` interface when they show the iterate recursion, initial condition, or metric. Do not inline low-level framework plumbing, such as custom interpolation class internals, unless those details are mathematically essential for human review. The setup module may still be imported for reusable problem objects and a lightweight availability check, but the notebook reader should not need to open `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py` to see the update rule or PEP definition. The numerical evidence section should import/use `matplotlib` and plot the sweep values against the candidate rate; when the rate is still unknown, plot the most plausible numerical pattern identified in Step 4 and clearly label it as a guess.

Do not add a compact final proof yet. Leave clear section headings for the later blocks so they can update the same notebook.

---

## Output

Report:
- Algorithm identified (`ALGO_NAME`, `PROBLEM_TYPE`)
- Convergence rates for N=1..7
- Conjectured rate formula
- Path to setup module
- Path to initialized notebook

**Next step**: `/pep-full-proof {ALGO_NAME}`
