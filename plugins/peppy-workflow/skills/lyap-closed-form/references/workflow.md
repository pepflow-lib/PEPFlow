# /lyap-closed-form: PEPFlow Block 5 — Find Closed-Form Lyapunov Function

Using the Lyapunov structure from Block 4, derive any unresolved coefficients and local certificate terms from symbolic difference identities, verify the analytic proof, and produce a human-readable notebook. Reuse applicable closed forms from earlier blocks when available; a completed analytic full-PEP proof or prior coefficient fit is not required. The default PEPFlow convention is that `V_k` has the sign that makes the sequence nonincreasing in the proof.

> $ARGUMENTS  (ALGO_NAME, e.g. `heavy_ball`)

---

## Environment

PEPFlow repo root: `$(git rev-parse --show-toplevel)/`
Python executable: `.venv/bin/python3`
Input: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json`
Output: `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` + printed LaTeX proof
Notebook: finalize the existing notebook created by Block 1

## Output Layout

Before creating files, read and follow [the shared output layout](../../../references/output-layout.md). Resolve the example paths below from the actual output notebook directory, including when it is under `examples_peppy/`.

---

## Reference Scope

When looking for reference examples, notebook structure, proof-writing patterns, or prompt skeletons, use only files under `examples_peppy/`. The `examples_peppy/_references/` subtree is explicitly allowed and may be used freely as reference material. Do not inspect or follow other repository example/reference files outside `examples_peppy/` for this workflow.

---

## Step 1 — Load State

Load the Block 4 state without requiring an earlier fit or a global full-PEP closed form:

```python
import json
import sympy as sp
import pepflow as pf

with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json") as fh:
    b4 = json.load(fh)
reconstruction = b4.get("numerical_reconstruction", {})
if not reconstruction.get("passed") or not b4.get("certificate_id") or (
    reconstruction.get("certificate_id") != b4["certificate_id"]
):
    raise ValueError("Recover and recheck the coherent Block 4 structure before derivation")
print("algo_name:", b4["algo_name"])
print("basis_templates:", b4.get("basis_templates", []))
print("unresolved_coefficients:", b4.get("unresolved_coefficients", []))
print("numerical_certificate_verified:", b4.get("numerical_certificate_verified", False))
print("analytic_full_pep_verified:", b4.get("analytic_full_pep_verified", False))
print("lyapunov_proof_verified:", b4.get("lyapunov_proof_verified", False))
known_sources = {name: b4.get(name) for name in ("lamb_code", "S_code", "coeff_code")}
require_analytic_full_pep = bool(b4.get("require_analytic_full_pep", False))
coefficient_formula_status = b4.get("coefficient_formula_status", "unresolved")
proof_checks = {name: False for name in (
    "step", "base", "boundary", "signs", "domain", "normalization")}
proof_arguments = {}
final_lyapunov_formula = None
final_expression_structure = None
derived_coeff_code = b4.get("coeff_code")
local_multiplier_code = None
remaining_unknowns = list(b4.get("unresolved_coefficients", []))
```

Read `basis_code`, optional `structure_code`, `basis_templates`, `expression_structure`, `unresolved_coefficients`, numerical coefficient/reconstruction evidence, the coherent Block 2 certificate, and its initial `closed_form_search` record. `lamb_code`, `S_code`, and `coeff_code` may be absent or null. Retain usable legacy formulas, but treat a legacy `proof_valid` flag or numerical formula agreement as diagnostic evidence only. If an old state lacks the coherent certificate or reconstruction evidence, follow the Block 2-4 compatibility checks and recover those prerequisites before this reader gate, without discarding useful formulas. Reuse a just-verified handoff only for unchanged inputs and sources; otherwise replay its saved-certificate and structure reconstruction checks before deriving from it. A stored `passed` flag alone does not revalidate changed inputs.

Run the dependent Python examples below in one process or notebook kernel. Adapt the algorithm-specific expressions into executable notebook cells; commented sketches or stored success flags are not completed checks. Missing coefficient formulas initiate derivation in this block. Return to Block 4 only when the basis or expression structure itself is insufficient.

---

## Step 2 — Set Up Symbolic Recursion Context

Create a minimal symbolic context encoding the actual algorithm update and every vector, function value, and constant term needed by the Block 4 structure. Use symbolic `k`, `N`, and algorithm parameters over the stated domain; finite-horizon matrices remain numerical evidence, not formulas at symbolic horizons.

```python
k_sp, N_sp = sp.symbols("k N", integer=True)
ctx_lyap = pf.PEPContext("lyap_recursion").set_as_current()
# Define the algorithm-specific abstract vectors, function/operator values,
# and update equations here, using only the problem's stated assumptions.
params_symbolic = {"k": k_sp, "N": N_sp}
# Add the actual algorithm parameters and their justified assumptions.
# For an unresolved scalar coefficient, retain an explicit function:
a_k = pf.Parameter("a_k")
params_symbolic["a_k"] = sp.Function("a")(k_sp, N_sp)
# Add separate mapped coefficients for k+1, local multipliers, and endpoints.
# Build V_k and V_k1 from the actual basis and known/unknown coefficients.
# Include function-value gaps and offsets present in expression_structure.
```

Represent unresolved coefficients inside PEPFlow expressions with `pf.Parameter` objects and map their names to the corresponding SymPy functions or expressions in `resolve_parameters`. This permits coefficient-equation discovery without requiring SymPy to infer that an undefined function is real. Substitute applicable known formulas and keep unresolved functions explicit. Load optional formula source only when it is needed, adapting its arguments to the symbolic context explicitly; do not use blind string replacement of horizon names or execute null source. A numerically fitted formula is a candidate until the analytic checks below establish its validity.

For the quadratic part, preserve `V_k = sum_{i,j} C_ij(k,N) * <v_i(k),v_j(k)>` with a symmetric coefficient matrix: an off-diagonal matrix entry contributes twice in a full double sum. Include all function-value and constant components, and separate initial, interior, and terminal cases. Use the `unresolved_coefficients` records to name unknown functions and their roles; do not replace missing coefficients by zeros. An empty quadratic basis has a 0-by-0 coefficient matrix (which JSON may store as `[]`); retain any nonzero function-value and constant terms at that index.

Introduce any still-unknown local interpolation multipliers and square-term coefficients alongside the Lyapunov coefficients. Their supports may be suggested by the numerical grouping, but their symbolic identities and signs must be proved. A valid local Lyapunov certificate need not reconstruct the entire global lambda table or a global closed-form decomposition of S.

If the Lyapunov expression uses additional iterates or auxiliary sequences, include them and their recurrences in the symbolic context. Do not impose unstated positivity assumptions on all parameters to make a symbolic calculation succeed.

---

## Step 3 — Symbolic Recursion: Step Identity

With the common nonpositive-residual convention, derive and then verify an identity of the form:

```text
V_{k+1} - V_k = sum_r mu_{k,r} * I_{k,r}
                  - sum_s alpha_{k,s} * ||s_{k,s}||^2
I_{k,r} <= 0, mu_{k,r} >= 0, alpha_{k,s} >= 0
```

Use the actual residual convention of the problem, including equality residuals and matrix-valued constraints where applicable. The resulting inequalities must imply `V_{k+1} <= V_k`, or an explicitly equivalent telescoping argument. A zero identity with the wrong sign direction is not a valid convergence proof.

Form `diff_step = V_k1 - V_k - step_contribution` after substituting the algorithm's updates. Extract equations from every scalar component, not just the Gram matrix. The following local helpers support both equation discovery and exact verification:

```python
def symbolic_components(expression, manager):
    value = manager.eval_scalar(pf.Scalar.zero() + expression, sympy_mode=True)
    gram = sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    functions = sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    offset = sp.simplify(sp.sympify(value.offset))
    return gram, functions, offset


def component_equations(expression, manager):
    gram, functions, offset = symbolic_components(expression, manager)
    return [sp.Eq(term, 0) for term in [*gram, *functions, offset] if term != 0]


def verify_symbolic_identity(name, expression, manager):
    gram, functions, offset = symbolic_components(expression, manager)
    exact_zero = all(term == 0 for term in [*gram, *functions, offset])
    print(f"{name} inner-product residual:", gram)
    print(f"{name} function-value residual:", functions)
    print(f"{name} constant residual:", offset)
    if not exact_zero:
        raise ValueError(f"{name} identity remains unresolved")
    return True

# After constructing the actual algorithm-specific V_k, V_k1 and contributions:
# pm_lyap = pf.ExpressionManager(ctx_lyap, resolve_parameters=params_symbolic)
# diff_step = V_k1 - V_k - step_contribution
# equations = component_equations(diff_step, pm_lyap)
# After solving and substituting the actual formulas:
# proof_checks["step"] = verify_symbolic_identity("Step", diff_step, pm_lyap)
```

Solve the coefficient equations or recurrences jointly for the unknown Lyapunov coefficients, local multipliers, and square coefficients. Use exact arithmetic, justified ansatzes, algebraic elimination, or recurrence solving as appropriate. Incorporate the base and terminal conditions from Steps 4-5 and the target bound's normalization before accepting a solution. Numerical samples can suggest a solution but cannot certify it.

A homogeneous solution such as `V_k = 0` is insufficient unless the actual base/terminal inequalities still establish the requested performance bound. Record remaining freedom and select a valid choice or family with proved domain and sign conditions; uniqueness is not required.

Substitute the derived formulas back into the original expressions and verify them for the claimed symbolic index and parameter domain. Show the actual `LHS`, `RHS`, and `diff` construction in each notebook check, with labeled matrix displays where required. Reuse the component helper only for extracting/checking those visibly constructed expressions. Reject nonzero function or constant residuals even when the Gram residual vanishes. Report unresolved recurrences or sign obligations precisely instead of setting an analytic proof flag.

---

## Step 4 — Base Case (k=0 or k=1)

Create a separate symbolic context for the actual initial step, including the correct starting index, initial condition, and any exceptional coefficients. Derive the base identity and the upper bound on the initial potential needed by the target theorem. Do not infer endpoint validity by substituting into a formula outside its proved interior domain.

```python
# Build the actual initial context, base_LHS, base_RHS, and pm_base.
# diff_base = base_LHS - base_RHS
# proof_checks["base"] = verify_symbolic_identity("Base", diff_base, pm_base)
```

Use the base equations as boundary conditions when solving the coefficient recurrences. Verify all Gram, function-value, and constant components exactly and justify the initial inequality, including the problem's normalization parameters. Keep this executable construction in the notebook and cover exceptional small horizons separately.

---

## Step 5 — Boundary Identity (Final Step)

Build a terminal symbolic context with symbolic horizon `N` and the actual performance metric. Derive the relation between the final potential and that metric, including every remaining interpolation, slack, or square term. A numerical certificate at `N_verify` and `np.allclose` are supporting diagnostics, not the final boundary proof.

```python
# Build the actual terminal context, terminal_LHS, terminal_RHS, and pm_terminal.
# diff_boundary = terminal_LHS - terminal_RHS
# proof_checks["boundary"] = verify_symbolic_identity(
#     "Boundary", diff_boundary, pm_terminal)
```

Together, the initial inequality, step decrease, and terminal inequality must imply the requested bound with its exact finite-horizon constant and parameter normalization. For a potential normalized to dominate the performance metric, show `performance_metric <= V_N <= V_0 <= target_bound`; otherwise write the explicitly equivalent telescoping argument for the chosen potential.

Derive any required local terminal multipliers or square coefficients jointly with the potential. This path does not require global `lamb_code` or `S_code` if the analytic Lyapunov proof can be completed directly. Preserve the numerical full-PEP evidence and its unresolved analytic status honestly.

If the identity or the boundary implication fails, inspect all scalar components, terminal/small-horizon cases, and normalization before revising the formulas. Keep useful exploration results and report the exact unresolved obligation; do not mark the Lyapunov proof verified.

Inventory the positivity, nonnegativity, and nonvanishing obligations actually used by the step, base, and final boundary inequalities. Once the relevant coefficient definitions exist, the agent may invoke the optional [localize-n-summation-proof](../../../optional/localize-n-summation-proof/SKILL.md) skill for a bottleneck in those obligations, a proof-critical sum/index identity lacking a generic symbolic audit, or an identified substantial simplification of a complex valid global sign proof. Briefly state the target and follow the canonical procedure within the current task/resource budget without waiting for a separate skill request. Skip concise valid arguments, unused signs, and autonomous localization disabled by the user.

Place any resulting lemma, sign reasoning, and exact local audit in the existing notebook before the final telescoping argument, and cite the lemma where its signs are used. Preserve the selected candidate during localization; this does not restrict the surrounding coefficient-discovery workflow. If localization fails, preserve any existing valid global argument and report the precise gap. Necessary signs must be justified before proof completion, but replacing an already valid global proof is not required.

---

## Step 6 — Assemble Human-Readable Proof

Once all three identities, required sign/domain arguments, and target normalization are verified, write the proof in a structured form:

```
Theorem: For the {ALGO_NAME} algorithm on {PROBLEM_TYPE} functions with {INITIAL_CONDITION},
         after N iterations: {PERFORMANCE_METRIC} ≤ {CONJECTURED_RATE}.

Proof:
Define V_k = (full closed-form expression in terms of special vectors with closed-form coefficients).
The proof outline must display this formula explicitly in LaTeX, including the valid
index range and any coefficient definitions such as a_k, theta_k, or beta_k.

1. (Base case) State the exact initial identity and justify the initial-potential
   bound using the stated initial condition and target normalization.

2. (Step recursion, k=1..N-1) V_{k+1} − V_k = λ_k * interp(x_k, x_{k+1}) + ... ≤ 0
   since interpolation inequalities are ≤ 0 and all duals λ_k ≥ 0.
   Therefore V_k is nonincreasing: V_N ≤ ... ≤ V_1 ≤ V_0.
   This nonincreasing direction is the convention; if the identity gives the
   opposite direction, redefine `V_k` with the opposite sign and update every
   boundary identity accordingly.
   This must be written as a detailed equation, not as an ellipsis-only summary:
   include every active interpolation residual family, every extra constraint
   residual, and every negative slack/square term that appears in the per-step
   certificate. Define the residual notation used in the equation (for example
   I_f(u,v), I_g(u,v), Lipschitz residuals, monotonicity residuals, and S_k).

3. (Boundary) State the exact terminal identity and show that the final potential
   controls the performance metric with the correct signs and scaling.
   Combine this with the initial bound and telescoping decrease to conclude
   {PERFORMANCE_METRIC} <= {CONJECTURED_RATE}.
```

Print the proof in both symbolic and LaTeX forms.

### Save proof status and formulas

Record the actual sign and domain arguments, boundary implication, and normalization evidence in `proof_arguments`, referring to the notebook derivation and its claimed domain. Populate `final_expression_structure` with the resolved interior, initial, terminal, function-value, and constant formulas using the Block 4 structure keys; do not leave named unknown functions in a supposedly completed structure. Keep the original discovery structure and numerical `structure_code` as sample evidence, distinct from the final analytic formulas and their executable notebook construction. Set the corresponding `proof_checks` entries only when those obligations are established. Retain a verified local multiplier formula separately from global `lamb_code`; proving a local Lyapunov certificate does not establish the full global lambda/S formula.

```python
# Set final_lyapunov_formula, final_expression_structure, derived_coeff_code,
# local_multiplier_code,
# remaining_unknowns, coefficient_formula_status, and proof_checks/proof_arguments
# from the actual proof. coeff_code may remain null if the resolved formulas
# and their executable notebook construction are recorded explicitly.
lyapunov_proof_verified = (
    all(proof_checks.get(name) is True for name in (
        "step", "base", "boundary", "signs", "domain", "normalization"))
    and bool(final_lyapunov_formula)
    and isinstance(final_expression_structure, dict)
    and set(final_expression_structure) == {
        "quadratic_convention", "interior", "initial", "terminal",
        "function_terms", "constant_terms"}
    and not remaining_unknowns
)
state = {
    **b4,
    "analytic_full_pep_verified": bool(b4.get("analytic_full_pep_verified", False)),
    "lyapunov_proof_verified": lyapunov_proof_verified,
    "require_analytic_full_pep": require_analytic_full_pep,
    "proof_checks": proof_checks,
    "proof_arguments": proof_arguments,
    "lyapunov_formula": final_lyapunov_formula,
    "discovery_expression_structure": b4.get("expression_structure"),
    "expression_structure": (final_expression_structure if final_expression_structure is not None
                             else b4.get("expression_structure")),
    "coeff_code": derived_coeff_code,
    "local_multiplier_code": local_multiplier_code,
    "coefficient_formula_status": (
        "verified" if lyapunov_proof_verified else coefficient_formula_status),
    "unresolved_coefficients": remaining_unknowns,
}
with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b5.json", "w") as fh:
    json.dump(state, fh, indent=2)
```

An incomplete derivation may still be saved for further work with `lyapunov_proof_verified: false` and explicit remaining obligations. Never infer analytic status from a legacy `proof_valid` flag. Keep `analytic_full_pep_verified` independent: it may remain false when the analytic Lyapunov proof succeeds. The final notebook execution, rendering, and evidence audit below are still required before reporting Block 5 complete. Preserve `require_analytic_full_pep` when the user explicitly requested the global analytic proof: a completed local Lyapunov proof does not close that separate objective while `analytic_full_pep_verified` is false.

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
6. S decomposition (LDL or direct, from Block 2), showing the true S certificate matrix with `pf.pprint_labeled_matrix` and its numerical reconstruction check; display a stored guessed S formula when available, with its actual candidate or analytic status
7. Partial sum construction with rank profile (from Block 3), with the `lyap`/partial-sum definition written explicitly in the notebook cell
8. Candidate vector generation and column-space filtering (from Block 4), retaining the visible `find_basis_with_sparsest_coefficients(...)` search cell and its executed output for each searched `k`: rank, selected basis labels, and near-zero coefficient count/total. Preserve the actual search inputs and settings, and any explanation and decomposition check for adopting a different basis; final basis reconstruction alone does not replace this search evidence.
9. Coefficient matrix extraction per k with fractions (from Block 4), displaying coefficient matrices with `pf.pprint_labeled_matrix`
10. Symbolic step recursion check (from Step 3 of this block), built with PEPFlow contexts, Scalars, and `pf.ExpressionManager`
11. Base case and boundary symbolic verification (Steps 4–5), built with PEPFlow contexts, Scalars, and `pf.ExpressionManager`, with base and boundary in separate markdown/code cells

The first code cell should keep ordinary imports at the top, then insert the repository root into `sys.path`, then import repo-local modules such as `pepflow` with an explicit `# noqa: E402`. This lets notebook execution use the repo-local package rather than a stale installed package while keeping Ruff's import-order rule intentional. Use paths anchored at the repository root inside the notebook so it executes correctly even when the kernel starts in `examples_peppy/{ALGO_NAME}`.

Write notebook code so it is friendly to static checks (`ruff` and `ty`) even when the notebook uses dynamic workflow artifacts. If a cell uses `exec(...)` to load generated helper functions, bind the expected names explicitly from `globals()` with type annotations immediately afterward, for example `V_k_basis: Callable[[int], list[Any]] = globals()["V_k_basis"]`. Guard dynamic imports from `importlib.util.spec_from_file_location(...)` with `if spec is None or spec.loader is None: raise ImportError(...)` before calling `exec_module`. Avoid bare `display(...)` calls unless `display` is imported explicitly, and simplify SymPy matrices elementwise with `sp.Matrix(...).applyfunc(sp.simplify)` rather than `sp.simplify(sp.Matrix(...))`.

Keep supporting Python modules friendly to `ty` as well. For functions that return structured JSON containing nested dictionaries, lists, and scalar values, annotate the output shape broadly enough, such as `dict[str, Any]`, or define a precise `TypedDict`; do not let `ty` infer a too-narrow union from the first few keys before later assigning nested entries like `lambda_groups`. For optional integration imports that may be absent from the local type-check environment, prefer installing the declared dependency; if the dependency is intentionally optional, use a narrow `# ty: ignore[unresolved-import]` on that import only, and keep any `# noqa: E402` import-order suppression separate and explicit.

When displaying dense or relaxed certificate matrices in the notebook, use `pf.pprint_labeled_matrix(...)` with the stored row and column names. For multiple lambda groups, display each group as a labeled matrix before printing any optional nonzero-entry fraction summary. Avoid replacing the labeled matrix display with manual nested-loop text dumps.

For the S decomposition/direct S formula cell, keep the output focused: display the true S matrix from the coherent certificate with `pf.pprint_labeled_matrix(...)`, display `S_formula` when one was actually found, and print the numerical reconstruction or candidate matrix comparison. If the global formula is unresolved, retain the initial search and verified numerical decomposition with `analytic_full_pep_verified: false`; do not invent `S_formula` or require one to finish the local Lyapunov proof. Avoid dumping both the guessed matrix and true matrix unless the comparison fails.

For the partial-sum/rank-profile cell, write out the actual `lyap = [...]`, `partial_sum = ...`, and update loop that defines the Lyapunov partial sums. Do not hide this definition behind `exec(b5['grouping_code'])` or another serialized-code shortcut; the notebook must show the mathematical construction before printing the rank profile.

For the coefficient extraction cell, use `pf.pprint_labeled_matrix(...)` to display coefficient matrices with the active basis-vector labels. When comparing decomposed coefficients against closed-form formulas, show both the decomposed matrix and the closed-form matrix as labeled matrices before printing the match check. Avoid raw `print(C)` or unlabeled NumPy matrix dumps for these outputs.

After the numerical coefficient extraction, preserve the expression structure and any fitted candidate or unresolved coefficient functions from Block 4. When coefficients are derived here, add visible cells showing the difference equations or recurrences, base/terminal conditions, normalization, and their solution. Before the final symbolic step verification, add a Markdown conclusion stating the resulting closed-form `V_k` in LaTeX and explaining that the next section verifies its one-step identity. The final theorem and conclusion must use the derived formulas, not an unresolved ansatz.

The `### Theorem` cell near the top of the notebook must explicitly state the final closed-form `V_k` formula, not merely the convergence rate. The `### Proof outline` cell must be mathematically self-contained enough that a reader can follow the proof without reading the code cells first. At a minimum, it must repeat the proof-critical parts of the final `V_k` formula and spell out the detailed `V_{k+1}-V_k` (or shifted `V_k-V_{k-1}`) identity, including all interpolation residuals, extra residuals, and slack/square terms. Do not replace these with phrases like "dual contributions", "certificate terms", or an ellipsis.

When the evaluated Lyapunov partial sums have nonzero function coordinates (`func_coords`), the closed-form `V_k` must include the corresponding function-value gap terms, such as `f(x_k)-f(x_star)` or `(f+g)(x_k)-(f+g)(x_star)`, with their exact coefficients. Do not present only the quadratic/inner-product part from `inner_prod_coords`; compare and report both the function-coordinate pattern and the inner-product coefficient matrix.

For symbolic step, base, and boundary identity cells, follow the package-native style used in `examples_peppy/_references/gd/gd_example_lyap.ipynb` and the relevant `examples_peppy/_references/.../*_example_lyap.ipynb` notebook: create an auxiliary `pf.PEPContext`, define symbolic parameters such as `k`, `N`, and algorithm parameters with `pf.Parameter`/SymPy symbols, define the symbolic iterates with PEPFlow `Vector`, `Parameter`, operator/function calls, form `LHS`, `RHS`, and `diff` as PEPFlow `Scalar` expressions, and use `pf.ExpressionManager` to extract and simplify the residual coordinates. Display residual matrices with `pf.pprint_labeled_matrix(...)`.

The symbolic verification cells must contain the actual symbolic calculation code in the notebook itself. They must not merely assert stored booleans from `b5`, call a helper such as `_closed_form_verify.py`, or replay a concrete-N verification from earlier blocks. Helper scripts may supplement the notebook, but each symbolic verification cell must visibly construct the symbolic context, the symbolic identity, and the simplified residual. For checks of PEPFlow Scalar expressions, extract and simplify `inner_prod_coords`, `func_coords`, and `offset` and verify all applicable components exactly; a zero Gram matrix alone is insufficient.

For separately created or reused files that justify coefficient signs or other proof conditions, apply the [proof verification rule](../../../references/output-layout.md#proof-verification-files-during-notebook-authoring): keep the necessary definitions/domains, actual identity construction and exact checks/results, and the sign implication in the main notebook. A verifier call alone is insufficient. Use existing cells or a short notebook appendix; elementary facts such as `1/k > 0` for `k >= 1` need no dedicated check. Supplementary exploration and redundant independent tests need not be copied.

Immediately after every symbolic verification heading, add a markdown cell with the exact LaTeX equation being verified before the code cell. This applies at least to `## Symbolic Step Recursion Verification`, `## Base Case and Boundary Symbolic Verification`, and `### Boundary Identity Symbolic Verification`. The equation cell should state the identity and say that the residual `$\mathrm{LHS}-\mathrm{RHS}$` should simplify to zero.

Keep the base case and boundary identity symbolic verifications in separate notebook cells, with a clear markdown heading before the boundary cell such as `### Boundary Identity Symbolic Verification`. Do not combine the base residual calculation and the boundary residual calculation in one long code cell.

For auxiliary symbolic contexts, distinguish Python variable names from rendered PEPFlow tags. Python identifiers may use snake case such as `A_step`, `A_base`, or `A_boundary`, but the rendered tags passed to PEPFlow objects should use clear math notation with braces, such as `tags=['A_{step}']`, `tags=['A_{base}']`, and `tags=['A_{boundary}']`. This avoids tag collisions with the main operator and prevents ambiguous notebook labels like `A_step(x_k)`.

For all notebook Markdown cells, use `$...$` for inline math and `$$...$$` for display math. Do not use `\(...\)` or `\[...\]` as notebook Markdown math delimiters. After notebook execution, inspect the final saved notebook in a notebook frontend or an HTML preview with its math renderer loaded. Visually check every Markdown cell containing math, including algorithm equations, the theorem, proof outline, Lyapunov formulas, and verification identities, for raw TeX delimiters, malformed formulas, missing equation operators or symbols, and clipping. Delimiter replacement, source scanning, and successful notebook execution alone do not establish correct rendering. Fix rendering defects and reinspect the affected cells; Markdown-only changes follow the rendered-inspection rule below. If rendered inspection is unavailable, leave the corresponding supplementary checklist evidence pending and report the incomplete review.

When generating markdown cells programmatically, protect LaTeX backslashes from Python escape sequences. Use raw strings or doubled backslashes for commands such as `\frac`, `\right`, `\le`, and `\operatorname`. Before reporting completion, scan the notebook source for control characters such as form-feed (`\f`) or carriage-return (`\r`) inside markdown cells; these usually indicate an escaped LaTeX command was corrupted and will cause KaTeX parse errors.

In markdown and displayed formulas, always brace subscripts and superscripts that are not single literal symbols: write `x_{0}`, `x_{k+1}`, `x_{k+1/2}`, `A_{k}`, and `V_{N}` rather than `x_0`, `x_k+1`, or `V_N`. This prevents notebook LaTeX parsing ambiguity and keeps rendered mathematical notation consistent.

Place the proof statement section immediately after the title/algorithm description and before the imports. Keep the proof section structurally clear: do not combine the theorem statement and proof into one large markdown cell. Use one unnumbered heading-only cell for `## Proof Statement`, never `## 10. Proof Statement`, one cell titled `### Theorem`, and one cell titled `### Proof outline`.

The `### Theorem` cell must not be only a rate statement. It must present the Lyapunov certificate `V_k` before or alongside the claimed guarantee, so a reader sees the theorem and certificate without having to search later diagnostic sections.

Do not add a final numerical/symbolic verification section if it only repeats the already verified boundary identity in the recreated concrete context. The boundary identity symbolic verification is the authoritative final identity verification; an extra `## Numerical Verification of Final Identity` section is optional only when it verifies a genuinely different end-to-end condition.

Before the final notebook execution, run static checks on the generated notebook and fix issues in the notebook source:

```bash
ruff check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb
uvx ty check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb
```

If `uv` is not available in the environment, use an installed `ty` executable instead:

```bash
ty check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb
```

Treat `uvx ty check ...` as the preferred self-contained command and `ty check ...` as the fallback for pip/conda environments where `ty` has already been installed.

After static checks pass, execute the final notebook end to end from a clean kernel before reporting completion:

```bash
mkdir -p examples_peppy/{ALGO_NAME}/supplementary/.runtime
export JUPYTER_RUNTIME_DIR="$(pwd)/examples_peppy/{ALGO_NAME}/supplementary/.runtime"
export TMPDIR="$(pwd)/examples_peppy/{ALGO_NAME}/supplementary/.runtime"
.venv/Scripts/python.exe -m jupyter nbconvert \
  --to notebook \
  --execute examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb \
  --output {ALGO_NAME}_example_lyap.ipynb \
  --output-dir examples_peppy/{ALGO_NAME}
```

On Windows PowerShell, set the same runtime directories before executing:

```powershell
New-Item -ItemType Directory -Force examples_peppy/{ALGO_NAME}/supplementary/.runtime | Out-Null
$runtime = (Resolve-Path examples_peppy/{ALGO_NAME}/supplementary/.runtime).Path
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

The `supplementary/.runtime/` directory is only for Jupyter/Python tool files such as kernel connection files. Keep required main-step certificates, basis data, dual values, and closed-form state under the notebook's sibling `state/`. Keep durable additional scripts, exploratory results, and supporting documents under `supplementary/` outside `.runtime/`.

If notebook execution fails, fix the notebook and rerun it. Do not report completion based only on a standalone script or a compact proof-only notebook.

Changes to executable notebook cells or proof dependencies require affected static checks and final notebook re-execution; Markdown-only edits require rendered inspection.

After the required final execution and rendered inspection, audit the saved notebook against all twelve items in Block 1's Notebook Lifecycle and the detailed requirements in Definition of Done below. Update the same sibling `supplementary/<notebook-stem>_checklist.md`; if resuming a notebook without a record, create it from the twelve-item list. For each item, record its original number and wording, status, actual cell IDs (or zero-based indices), and evidence for every required part. For item 8 on the numerical-discovery path, verify the documented initial closed-form attempt, the coherent numerical lambda/S checks and decomposition, and explicit unresolved global analytic status; require the completed analytic Lyapunov proof in items 11-12 rather than a separate global full-PEP closed form. In particular, item 6 needs both numerical values and the comparison plot, item 7 needs both dense and relaxed proof solves, and item 12 needs separate step, base, and boundary evidence. Headings, TODOs, stored success flags, and execution counts alone do not establish completion.

Use the existing execution, static-check results, and rendered inspection rather than repeating them solely for the checklist. Record the notebook path, reviewed block, and SHA-256 of the final saved notebook. Any subsequent notebook or proof-dependency edit requires marking affected entries `pending` until rechecked and updating the record; executable and Markdown-only changes follow the validation rules above. The final checklist hash must match the delivered notebook. Keep this record and its maintenance code outside the notebook, PDF/TeX, and routine completion report. Fix omissions or failed checks before claiming completion; if any required item remains missing, failed, or unverified, report it concisely and leave Block 5 incomplete.

After the notebook executes, confirm its path and print the final Lyapunov function and convergence theorem in mathematical notation.

---

## Definition of Done

This block is not complete until all of the following are true:

1. `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` contains separate cells for every Step 1-7 section in this workflow.
2. The notebook is not a compact proof-only artifact. It must include the diagnostic trail:
   - state loading
   - symbolic recursion context
   - dense/relaxed certificate inspection with labeled matrix displays via `pf.pprint_labeled_matrix`
   - S decomposition or direct S formula verification with a labeled true S matrix, its numerical reconstruction check, and the actual status of any available global formula
   - explicit partial sum reconstruction defining `lyap` and `partial_sum` in the notebook cell
   - rank profile
   - special vector/basis reconstruction from Block 4
   - the actual Block 4 sparse-basis search call visible in an executable notebook cell, with executed per-k rank, selected-basis, and near-zero-count output; candidate filtering, saved-state replay, or a final basis definition alone is insufficient
   - coefficient extraction and formula verification with labeled decomposed and closed-form coefficient matrices
   - markdown conclusion after coefficient extraction stating the closed-form Lyapunov function `V_k`
   - if `func_coords` are nonzero, the closed-form `V_k` includes all function-value gap terms with exact coefficients
   - theorem markdown near the top that explicitly states the final closed-form Lyapunov function `V_k`, including terminal/special cases
   - proof outline markdown near the top that explicitly states the final `V_k` formula
   - proof outline markdown near the top that explicitly states the detailed `V_{k+1}-V_k` or `V_k-V_{k-1}` equation with all residual and slack terms
   - proof outline markdown explicitly states why the chosen sign convention makes `V_k` nonincreasing (or otherwise gives the equivalent telescoping direction needed for the final bound); do not accept a sign-reversed Lyapunov statement even if all symbolic residual matrices are zero
   - symbolic step identity implemented in the notebook cell itself with symbolic PEPFlow expressions and `pf.ExpressionManager`; no stored-boolean-only checks
   - base identity implemented in the notebook cell itself with symbolic PEPFlow expressions and `pf.ExpressionManager`; no stored-boolean-only checks
   - boundary identity implemented in the notebook cell itself with symbolic PEPFlow expressions and `pf.ExpressionManager`; no stored-boolean-only checks
   - PEPFlow Scalar-expression verification cells display and check `inner_prod_coords`, `func_coords`, and `offset`, including function-value and constant terms wherever present
   - markdown equation cells immediately after each check heading stating the identity being verified
   - separate proof statement cells: unnumbered `## Proof Statement`, `### Theorem`, and `### Proof outline`
   - all Markdown cells containing math use `$...$` for inline math and `$$...$$` for display math, with final visual inspection confirming correctly rendered equations, no raw TeX delimiters shown as text, and no malformed, missing, or clipped mathematical content
3. All three identities must be verified by executable symbolic code in the notebook:
   - step identity residual is exactly zero or simplifies to zero through `pf.ExpressionManager` coordinates using symbolic `k`, `N`, and algorithm parameters where applicable
   - base identity residual is exactly zero or simplifies to zero through `pf.ExpressionManager` coordinates using symbolic `N` and algorithm parameters where applicable
   - boundary identity residual is exactly zero or simplifies to zero through `pf.ExpressionManager` coordinates using symbolic `N` and algorithm parameters where applicable
   - the code cells visibly build `LHS`, `RHS`, and `diff`; a call to a helper script or an assertion of a stored state flag does not satisfy this requirement
   - after the residual identities are zero, the notebook checks the inequality direction implied by the residual signs and nonnegative multipliers, and confirms the final boundary step discards terms in the correct direction for the claimed rate
   - sign and domain conditions are established over the claimed range, and the base/terminal conditions yield the target finite-horizon bound and normalization; a homogeneous zero-potential solution alone does not satisfy this requirement
4. `ruff check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` must pass for this generated notebook. The type check must also pass, using either `uvx ty check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` if `uv` is available, or `ty check examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` otherwise.
5. The notebook must be executed with `jupyter nbconvert --execute` before the block is reported complete.
6. If notebook execution or static checks fail, fix the notebook and rerun the failing command.
7. Store any newly needed helper verification script in the notebook's sibling `supplementary/`, for example `examples_peppy/{ALGO_NAME}/supplementary/`, and keep notebook calls or references consistent with that location. The proof-critical symbolic calculations must still appear in the notebook, including those used from separately created or reused sign/domain verification files. Check their definitions, actual calculations/results, and proof implications in the relevant existing supplementary checklist entries; reuse evidence already present rather than adding duplicate cells or a new checklist.
8. Save durable Block 5 state to `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b5.json`. Set `lyapunov_proof_verified` only after all analytic proof obligations above are established; retain numerical-certificate and analytic-full-PEP statuses separately.
9. The supplementary evidence checklist verifies all twelve Notebook Lifecycle items against the final saved notebook and the detailed requirements above; no required content or check remains missing, failed, or unverified.

---

## Output

Report:
- The closed-form Lyapunov function `V_k` in mathematical notation
- Confirmation that all three symbolic identities (step, base, boundary) are zero
- Path to the generated notebook `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb`
- The LaTeX theorem statement
- Separate numerical-certificate, analytic-full-PEP, and analytic-Lyapunov proof statuses; a completed Lyapunov proof may have an unresolved global full-PEP formula

If the analytic Lyapunov proof is incomplete, report the exact unresolved coefficients, identities, sign/domain conditions, or boundary normalization instead of a completion claim. If `require_analytic_full_pep` is true and that proof remains unverified, report the remaining global proof obligation explicitly even when the local Lyapunov proof is complete.

After successfully completing Block 5, include this optional next-step note in the user-facing completion report:

> To generate a theorem-and-proof PDF and matching TeX source from this Jupyter notebook, use the optional `pdf-from-ipynb` skill.

Show `$pdf-from-ipynb <notebook-path>`, replacing `<notebook-path>` with the actual completed notebook path. This is an informational handoff; PDF export is not required to complete Block 5. Invoke the skill only when the user has requested the export.

This completes the 5-block PEPFlow workflow: algorithm definition → numerical proof → Lyapunov function → human-verifiable convergence theorem.
