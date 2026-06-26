# /pep-full-proof: PEPFlow Block 2 — Finding Full-PEP-Style Proof

Find a tight performance guarantee with explicit dual certificates (λ, S), enforce sparsity, and verify a closed-form algebraic proof.

> $ARGUMENTS  (ALGO_NAME, e.g. `heavy_ball`)

---

## Environment

PEPFlow repo root: `$(git rev-parse --show-toplevel)/`
Python executable: `.venv/bin/python3`
Input: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json`
Output: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json`
Notebook: update `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb`

---

## Reference Scope

When looking for reference examples, notebook structure, proof-writing patterns, or prompt skeletons, use only files under `examples_peppy/`. The `examples_peppy/_references/` subtree is explicitly allowed and may be used freely as reference material. Do not inspect or follow other repository example/reference files outside `examples_peppy/` for this workflow.

---

## Step 1 — Load State

```bash
.venv/bin/python3 -c "
import json
state = json.load(open('examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json'))
print('algo_name:', state['algo_name'])
print('problem_type:', state['problem_type'])
print('obj_tag:', state['obj_tag'])
print('params_json:', state['params_json'])
print('N_verify:', state['N_verify'])
print('conjectured_rate:', state['conjectured_rate'])
"
```

Extract: `ALGO_NAME`, `OBJ_TAG`, `PARAMS_JSON`, `N_VERIFY` (default 4).

---

## Step 2 — Dense Solve

Run a dense solve at `N = N_VERIFY`:

```bash
cd "$(git rev-parse --show-toplevel)" && \
mkdir -p examples_peppy/{ALGO_NAME}/state && \
.venv/bin/python3 -m pepflow.pep_runner \
    --module examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py \
    --N {N_VERIFY} \
    --params '{PARAMS_JSON}' \
    --output examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_dense.json
```

Read `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_dense.json`. Display:
- `opt_value` — compare to conjectured rate
- a compact summary of structurally important entries in each function/operator inequality dual group, such as `Monotone Operator Inequality` or `Lipschitz Operator Inequality`
- a compact summary of the S matrix structure, such as rank, dominant nonzero pattern, or candidate vector form
- `basis_vectors`

`pf.pprint_labeled_matrix` is a signature PEPFlow display API, but do not use it to dump every dense and relaxed raw certificate matrix by default. Use it where the labeled matrix is proof-bearing and readable: closed-form candidate λ matrices, S candidate/decomposition matrices, Lyapunov coefficient matrices, and proof-residual matrices. For raw dense/relaxed certificates, prefer compact summaries of active/nonzero entries unless the user asks for the full labeled tables.

---

## Step 3 — Detect and Enforce Sparsity

Inspect the dense λ for near-zero entries. Build a relaxation that drops all small entries.
For example, if only the consecutive (i, i+1) index pairs and (star, j) pairs seem significant, then try something like below.

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import json, numpy as np

with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_dense.json") as fh:
    data = json.load(fh)

N = data["N"]
row_names = data["lambda_row_names"]
col_names = data["lambda_col_names"]
lamb = np.array(data["lambda_matrix"])
OBJ_TAG = "{OBJ_TAG}"

def idx(tag, N=N):
    s = tag.split("_")[1]
    return int(s) if s.isdigit() else N + 1

# Hypothesis 1: keep only consecutive (i, i+1) and (x_star, x_j) pairs
relaxed = []
for ri in row_names:
    i = idx(ri)
    for ci in col_names:
        j = idx(ci)
        if not ((i + 1 == j and i < N) or i == N + 1):
            relaxed.append(f"{OBJ_TAG}:{ri},{ci}")

print("Hypothesis 1 relaxation (", len(relaxed), "constraints dropped):")
print(json.dumps(relaxed))
EOF
```

Test Hypothesis 1:

```bash
cd "$(git rev-parse --show-toplevel)" && \
mkdir -p examples_peppy/{ALGO_NAME}/state && \
.venv/bin/python3 -m pepflow.pep_runner \
    --module examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py \
    --N {N_VERIFY} \
    --params '{PARAMS_JSON}' \
    --relaxed '[... paste hypothesis 1 list ...]' \
    --output examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_relaxed.json && \
.venv/bin/python3 -c "
import json
dense = json.load(open('examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_dense.json'))['opt_value']
relax = json.load(open('examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_relaxed.json'))['opt_value']
print(f'Dense: {dense:.8f}  Relaxed: {relax:.8f}  Preserved: {abs(dense-relax)<1e-5}')
"
```

- **Preserved**: use `_relaxed.json` going forward.
- **Not preserved**: expand to Hypothesis 2 — also include skip-one pairs (`|i−j| == 2`) in the keep-set, retest.

**Find pattern at your discretion**: Consecutive index pairs are often, but not always, the right choice. For example, there are cases where (N, j) index pairs should be used. Inspect the dense λ and use your judgement to include the important-looking ones.

**Nontrivial checkpoint**: If no small sparsity pattern can be found that preserves the rate (even expanded hypothesis fails), display the dense λ fully and ask the user which entries look structurally important.

---

## Step 4 — Inspect Relaxed λ and Guess Closed Form

Try using the limited-denominator fraction expression to conjecture analytical form.

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import numpy as np, json, fractions

with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_relaxed.json") as fh:
    data = json.load(fh)

N = data["N"]
row_names = data["lambda_row_names"]
col_names = data["lambda_col_names"]
lamb = np.array(data["lambda_matrix"])

def idx(tag, N=N):
    s = tag.split("_")[1]
    return int(s) if s.isdigit() else N + 1

print(f"Non-zero λ entries (N={N}):")
for i, ri in enumerate(row_names):
    for j, ci in enumerate(col_names):
        v = lamb[i, j]
        if abs(v) > 1e-6:
            frac = fractions.Fraction(v).limit_denominator(1000)
            print(f"  λ({ri},{ci}) = {v:.6f}  ≈  {frac}")
EOF
```

From the printed fractions, observe the pattern indexed by (i, j, N). Propose a `lamb(ri, ci)` function. Verify it:

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import numpy as np, json

with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_relaxed.json") as fh:
    data = json.load(fh)

N = data["N"]
row_names = data["lambda_row_names"]
col_names = data["lambda_col_names"]
lamb_sol = np.array(data["lambda_matrix"])

def idx(tag, N=N):
    s = tag.split("_")[1]
    return int(s) if s.isdigit() else N + 1

def lamb(ri, ci, N=N):
    i, j = idx(ri), idx(ci)
    # TODO: fill in closed-form candidate
    # Example (GD-like):  return j / (2*N + 1 - j) if i + 1 == j and i < N else 0
    return 0

lamb_cand = np.array([[float(lamb(ri, ci)) for ci in col_names] for ri in row_names])
print("Max residual:", np.max(np.abs(lamb_cand - lamb_sol)))
print("Matches:", np.allclose(lamb_cand, lamb_sol, atol=1e-4))
EOF
```

**Algorithm parameters**: The analytical values may not always be a nice rational number. In such cases, consider building connection with the parameters used in the algorithm definition (update rule).

**Nontrivial checkpoint**: If no clean formula is apparent after careful inspection, present the table to the user and ask for insight on the pattern before continuing.

---

## Step 5 — Decompose S

### 5a — LDL decomposition

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import pepflow as pf, numpy as np, sympy as sp, importlib.util, json
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_relaxed.json") as fh:
    data = json.load(fh)
N = sp.S(data["N"])
params_sp = {k: sp.S(v) if isinstance(v, int) else sp.Rational(v)
             for k, v in json.loads('{PARAMS_JSON}').items()}

spec = importlib.util.spec_from_file_location("setup",
    "examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
ctx, pb, obj = mod.get_pep_setup(N, params_sp)
result = pb.solve(resolve_parameters=params_sp)

S_sol = result.get_gram_dual_matrix()
basis = ctx.basis_vectors()
D, ell = ldl_decompose_with_reversed_basis(S_sol, basis, print_output=True)

print("\nD diagonal:", [round(float(D[i,i]),6) for i in range(D.shape[0])])
print("ell vectors:", [str(e) for e in ell])
EOF
```

Inspect `D` diagonal — near-zero entries can be ignored. Note which `ell[k]` correspond to significant diagonal entries. The decomposition gives `S = Σ D[k,k] * ell[k]²`.

### 5b — Direct guess for low-rank S

When S is of low-rank (single squared term), guess something like `S = c * (A(x_N) - α*(x_0 - x_star))²` and verify:

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import pepflow as pf, numpy as np, sympy as sp, importlib.util, json
# ... (load ctx, pb, obj, result as above) ...
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
S_sol_np = np.array(data["S_matrix"])

# Define S_guess as a pf.Scalar expression and verify:
# S_guess = (obj(ctx[f"x_{N}"]) - sp.Rational(1,1)/(alpha*N) * (ctx["x_0"]-ctx["x_star"])) ** 2
# S_guess_np = pm.eval_scalar(S_guess).inner_prod_coords
# print("S matches:", np.allclose(S_guess_np, S_sol_np, atol=1e-4))
EOF
```

**Nontrivial checkpoint**: If neither LDL nor a direct guess produces a clean decomposition, show the S matrix to the user and ask for suggestions.

---

## Step 6 — Verify Full Proof Identity

Assemble the proof identity:
`performance_metric ≤ τ * initial_condition` via
`perf - τ*IC + interp_sum + extra_constraint_sum - S_guess = 0`

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import pepflow as pf, numpy as np, sympy as sp, itertools, importlib.util, json

N_int = {N_VERIFY}
N = sp.S(N_int)
params_sp = {k: sp.S(v) if isinstance(v, int) else sp.Rational(v)
             for k, v in json.loads('{PARAMS_JSON}').items()}

spec = importlib.util.spec_from_file_location("setup",
    "examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
ctx, pb, obj = mod.get_pep_setup(N, params_sp)
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)

with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_relaxed.json") as fh:
    data = json.load(fh)
row_names = data["lambda_row_names"]
col_names = data["lambda_col_names"]
tau_sol = data["tau_sol"]

def lamb(ri, ci, N=N_int):
    # paste verified closed form from Step 4
    return 0

# 1. Interpolation sum
interp_sum = pf.Scalar.zero()
for ri, ci in itertools.product(row_names, col_names):
    c = lamb(ri, ci)
    if c != 0:
        interp_sum += c * obj.interp_ineq(ri, ci)

# 2. LHS = perf - tau * IC  (adjust rate formula)
x_N, x_0, x_star = ctx[f"x_{N_int}"], ctx["x_0"], ctx["x_star"]
R = pf.Parameter("R")
LHS = obj(x_N) - obj(x_star) - sp.S(tau_sol) * (x_0 - x_star)**2

# 3. diff = LHS - interp_sum + S_guess  (should be zero)
# S_guess = ... (paste from Step 5)
diff = LHS - interp_sum  # + S_guess when ready

diff_matrix = pm.eval_scalar(diff).inner_prod_coords
print("Proof valid:", np.allclose(diff_matrix, 0, atol=1e-5))
if not np.allclose(diff_matrix, 0, atol=1e-5):
    pf.pprint_str(diff.repr_by_basis(ctx, sympy_mode=True,
                  resolve_parameters={"L": sp.Symbol("L")}))
EOF
```

Iterate on `lamb()` and `S_guess` until `Proof valid: True`.

---

## Step 7 — Save State

```bash
cd "$(git rev-parse --show-toplevel)" && \
.venv/bin/python3 - <<'EOF'
import json, numpy as np, os
os.makedirs("examples_peppy/{ALGO_NAME}/state", exist_ok=True)

b1 = json.load(open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json"))
relaxed_data = json.load(open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_relaxed.json"))

# Collect the closed-form lambda as Python source code (multi-line string).
# This will be used by Blocks 3-5 to recreate the proof.
lamb_code = """
def lamb(ri, ci, N=N_int):
    # TODO: paste verified closed form here
    return 0
"""

# Collect S decomposition info as Python source code.
S_code = """
# TODO: paste verified S_guess definition here
# S_guess = ...
"""

state = {
    **b1,
    "N_verify": relaxed_data["N"],
    "opt_value": relaxed_data["opt_value"],
    "tau_sol": relaxed_data["tau_sol"],
    "relaxed_constraints": relaxed_data.get("relaxed_constraints", []),
    "lambda_row_names": relaxed_data["lambda_row_names"],
    "lambda_col_names": relaxed_data["lambda_col_names"],
    "lambda_matrix": relaxed_data["lambda_matrix"],   # nested list
    "S_matrix": relaxed_data["S_matrix"],             # nested list
    "S_row_names": relaxed_data["S_row_names"],
    "S_col_names": relaxed_data["S_col_names"],
    "basis_vectors": relaxed_data["basis_vectors"],
    "lamb_code": lamb_code,      # Python source for lamb() function
    "S_code": S_code,            # Python source for S_guess expression
    "S_decomp_type": "ldl",      # "ldl" or "direct"
    "proof_valid": True,
}
with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json", "w") as fh:
    json.dump(state, fh, indent=2)
print("State saved to examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json")
EOF
```

---

## Step 8 — Update Lyapunov Notebook

Open the notebook created by Block 1 and update the proof-certificate sections. Follow the corresponding middle sections of `examples_peppy/_references/gd/gd_example_lyap.ipynb`.

Add or replace cells for:
- dense solve at `N_VERIFY`, with objective value, basis vectors, and compact summaries of active/nonzero entries in each lambda/function-class inequality group
- relaxation construction and preserved-optimum check
- relaxed certificate summaries, again focusing on active/nonzero entries and the preserved-optimum check rather than dumping all raw matrices
- nonzero relaxed lambda entries and the verified closed-form `lamb(...)`, including labeled candidate lambda matrices via `pf.pprint_labeled_matrix(...)`
- S decomposition or direct S formula, including a labeled S candidate matrix and the matrix match check
- fixed-N full proof identity check, including a labeled proof-residual matrix

Keep the Block 1 setup and numerical-evidence cells intact unless they are wrong. The notebook should remain executable after this update, although later Lyapunov sections may still contain placeholder headings.

---

## Output

Report:
- The relaxed constraint set (which λ entries are active)
- The closed-form `lamb(ri, ci)` formula
- The S decomposition (LDL diagonal values and `ell` vectors, or direct formula)
- Confirmation that `Proof valid: True`
- Confirmation that the notebook was updated through the proof-certificate sections

**Next step**: `/lyap-define {ALGO_NAME}`
