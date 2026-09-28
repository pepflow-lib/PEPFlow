# /lyap-vectors: PEPFlow Block 4 — Identifying Special Vectors

Using the Lyapunov partial sums from Block 3, find which special vectors span each V_k and retain numerical coefficient matrices with checked reconstructions. Coefficient fitting is optional: pass the basis pattern and explicit unknown coefficient functions to Block 5 when formulas remain unresolved.

> $ARGUMENTS  (ALGO_NAME, e.g. `heavy_ball`)

---

## Environment

PEPFlow repo root: `$(git rev-parse --show-toplevel)/`
Python executable: `.venv/bin/python3`
Input: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json`
Output: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json`
Notebook: update `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb`

## Output Layout

Before creating files, read and follow [the shared output layout](../../plugins/pepflow-workflows/references/output-layout.md). Resolve the example paths below from the actual output notebook directory, including when it is under `examples_peppy/`.

---

## Reference Scope

When looking for reference examples, notebook structure, proof-writing patterns, or prompt skeletons, use only files under `examples_peppy/`. The `examples_peppy/_references/` subtree is explicitly allowed and may be used freely as reference material. Do not inspect or follow other repository example/reference files outside `examples_peppy/` for this workflow.

---

## Step 1 - Load the Coherent Certificate and Rebuild Partial Sums

Use the numerically checked Block 3 certificate even when `lamb_code`, `S_code`, or an analytic full-PEP proof is absent. Keep `numerical_certificate_verified`, `analytic_full_pep_verified`, and `lyapunov_proof_verified` separate. A legacy `proof_valid` flag alone does not establish any all-parameter analytic claim. Recover missing legacy numerical checks/source from the actual verified earlier cells before proceeding; retain usable analytic formulas without requiring their rediscovery.

Read the selected certificate's `rank_search` and its notebook-relative `evidence_path` (normally `supplementary/rank_search.json`) from Block 3. Use the recorded fixed boundary exclusions when interpreting the basis pattern; equal ranks across horizons are evidence for this search, not a common-basis or reconstruction result. Block 4 owns the basis and full-expression reconstruction gate. For a legacy B3 state without `rank_search`, retain the original one-index exclusion at each end and its existing verified handoff; do not invent cross-horizon confirmation.

Run the Python fragments below in order in one process or notebook kernel, from the selected repository environment. Rebuild the setup without solving, verify the saved certificate's identity, provenance, coordinate order, normalization, complete scalar/PSD dual inventory, and numerical checks, then replay its verified decomposition/grouping source. If current inputs or sources differ, return to Blocks 2-3 for a complete coherent replacement and revalidation; do not splice old lambda with new S, erase missing PSD values, or rerun a solver merely to read this certificate.

```python
import json
from pathlib import Path
import importlib.util
import numpy as np
import sympy as sp
import pepflow as pf
from pepflow.lyapunov_utils import (
    vectors_in_column_space, find_symmetric_coefficient_matrix,
    find_basis_with_sparsest_coefficients, select_independent_subset,
)

REPO_ROOT = Path.cwd().resolve()  # Run from the selected repository root.
NOTEBOOK_DIR = REPO_ROOT / "examples_peppy" / "{ALGO_NAME}"
# Use the actual selected notebook directory for a custom destination.
state_dir = NOTEBOOK_DIR / "state"
b3 = json.loads((state_dir / "{ALGO_NAME}_b3.json").read_text(encoding="utf-8"))
certificate = b3
N_int = b3["N_verify"]
N = sp.S(N_int)
params = json.loads(b3["params_json"])
params_sp = {
    name: (sp.Rational(value) if isinstance(value, str) else
           sp.nsimplify(value, rational=True, tolerance=1e-9)
           if isinstance(value, float) else sp.S(value))
    for name, value in params.items()
}
relaxed = list(b3["relaxed_constraints"])
setup_path = NOTEBOOK_DIR / "{ALGO_NAME}_setup.py"
spec = importlib.util.spec_from_file_location("setup", str(setup_path))
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot import setup: {setup_path}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ctx, pb, obj = mod.get_pep_setup(N, params_sp)
pb.set_relaxed_constraints(relaxed)
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)

# These are the exact sources executed and checked by Block 3. The checker
# rebuilds every scalar/PSD contribution from the saved snapshot; it does not
# fabricate a PEPResult and none of these sources calls a solver.
certificate_checked = False
grouping_checked = False
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    source = b3.get(field)
    if not isinstance(source, str) or not source.strip():
        raise ValueError(f"Recover and verify missing Block 3 source: {field}")
    exec(compile(source, f"<Block-3-{field}>", "exec"), globals())
    if field == "certificate_check_code":
        assert certificate_checked, "The complete saved certificate did not pass"
    if field == "grouping_code":
        assert grouping_checked, "Partial-sum coverage/sign checks did not pass"

rank_tolerance = b3.get("rank_tolerance", 1e-4)
reconstruction_tolerance = b3.get("reconstruction_tolerance", 1e-5)
reconstruction_rtol = b3.get("reconstruction_rtol", 1e-5)
ranks = [int(np.linalg.matrix_rank(
    pm.eval_scalar(Vk).inner_prod_coords.astype(float), tol=rank_tolerance))
    for Vk in lyap]
assert ranks == b3["rank_profile"]
assert len(lyap) == N_int + 1
rank_search = b3.get("rank_search")
if rank_search is None:
    a, b = 1, 1  # Legacy B3 handoff: V_0 and V_N may be exceptional.
else:
    assert rank_search["status"] == "confirmed", "Return to Block 3 rank recovery"
    assert rank_search["selected_certificate_id"] == b3["certificate_id"]
    assert N_int in rank_search["confirmed_horizons"]
    assert len(set(rank_search["confirmed_horizons"])) >= 2
    exclusions = rank_search["boundary_exclusions"]
    a, b = exclusions["left"], exclusions["right"]
    assert all(type(count) is int and 0 <= count <= 2 for count in (a, b))
    assert isinstance(rank_search["evidence_path"], str) and rank_search["evidence_path"]
    rank_evidence = json.loads(
        (NOTEBOOK_DIR / rank_search["evidence_path"]).read_text(encoding="utf-8"))
    assert rank_evidence["summary"] == rank_search, "Rank evidence differs from the handoff"
    selected_samples = [s for s in rank_evidence["samples"]
                        if s["certificate_id"] == b3["certificate_id"]]
    assert len(selected_samples) == 1
    selected_sample = selected_samples[0]
    assert selected_sample["N"] == N_int and selected_sample["rank_profile"] == ranks
    assert selected_sample["recipe_id"] == rank_search["recipe_id"]
    assert selected_sample["rank_convention"] == rank_search["rank_convention"]
interior_indices = list(range(a, N_int - b + 1))
exceptional_indices = [k for k in range(N_int + 1) if k not in interior_indices]
if rank_search is not None:
    assert len(interior_indices) >= 3
    assert all(ranks[k] == rank_search["rank"] for k in interior_indices)
for k, Vk in enumerate(lyap):
    evaluated = pm.eval_scalar(Vk)
    for actual, saved in (
        (evaluated.inner_prod_coords, b3["lyap_inner_prod_coords"][k]),
        (evaluated.func_coords, b3["lyap_func_coords"][k]),
        (evaluated.offset, b3["lyap_offsets"][k]),
    ):
        actual = np.asarray(actual, dtype=float)
        saved = np.asarray(saved, dtype=float)
        assert actual.shape == saved.shape
        assert np.allclose(actual, saved, atol=reconstruction_tolerance,
                           rtol=reconstruction_rtol)
print("Rank profile (sanity check):", ranks)
```

The checker consumes `certificate`, `ctx`, `pb`, `obj`, `params_sp`, `N_int`, and `REPO_ROOT`. It recomputes the certificate ID, source/label/inventory checks, numerical residuals, and decomposition checks, and produces `S_sol`, `basis`, `tol`, the named weighted interpolation/extra terms, and `extra_duals`. The decomposition and grouping sources must use that same snapshot, preserve all residual families and PSD contributions, and revalidate Block 3 coverage and the selected nonincreasing sign convention. The executed grouping checks set `grouping_checked` from their actual outcome; a constant rank or a literal success assignment cannot substitute for them. Use the original tolerances; do not loosen them to make a handoff pass.

Check that the imported `pepflow` and setup/helper sources are the intended versions before reconstruction; restart a stale kernel after source changes. If a continuing kernel already has the verified same certificate/context/partial sums, reuse them only after checking unchanged inputs, source, coordinate order, grouping, and decomposition. The notebook still displays the actual certificate, decomposition, and partial-sum calculations as required by the earlier blocks; an `exec` call or success flag alone is not their presentation.

---

## Step 2 — Build Candidate Special Vectors

Create a rich candidate set from all tagged vectors, basis vectors, and their pairwise differences:

```python
# (continuing — lyap, ctx, pm, params_sp available)
from itertools import combinations

# Start with basis vectors and all tagged iterates
candidates = list(ctx.basis_vectors())
for tag in [f"x_{i}" for i in range(N_int + 1)] + ["x_star", "y_0"]:
    try:
        v = ctx[tag]
    except (KeyError, ValueError):
        continue
    if all(v is not previous for previous in candidates):
        candidates.append(v)

# Optionally add gradient evaluations if obj is a function:
# for i in range(N_int + 1):
#     try:
#         xi = ctx[f"x_{i}"]
#         candidates.append(obj.grad(xi))
#     except (KeyError, ValueError):
#         pass

# Pairwise differences
base = list(candidates)
for i, j in combinations(range(len(base)), 2):
    candidates.append(base[i] - base[j])

print(f"Total candidates: {len(candidates)}")
print("Candidate labels:", [str(v) for v in candidates[:20]], "...")
```

If the problem has domain-specific vectors (e.g., auxiliary iterates `z_k`), add them explicitly to the initial set. The user may suggest additional candidates via the optional argument to this command.

---

## Step 3 — Filter to Column Space of Each V_k

For each retained k in `a <= k <= N-b`, first identify which candidates lie in `col(V_k)`. The recorded exclusions allow up to two exceptional indices at each end, counting V_0 and V_N; use a separate basis for any exceptional index that does not fit the interior pattern. Then use `find_basis_with_sparsest_coefficients` to choose a rank-spanning subset whose quadratic coefficient matrix is as sparse as possible. The basis is not unique; this step picks a reproducible, interpretable coordinate system rather than a canonical mathematical basis.

```python
# (continuing — lyap, candidates, pm, ctx, params_sp available)

from pepflow.lyapunov_utils import find_basis_with_sparsest_coefficients

spanning_by_k = {}
basis_by_k = {}
coeff_by_k = {}
coeff_inputs = {}
search_tolerances = dict(zero_tol=1e-6, indep_tol=1e-7, span_tol=1e-5)
for k in interior_indices:
    rank_k = ranks[k]
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
        **search_tolerances,
    )
    if len(basis) != rank_k:
        raise ValueError(f"k={k}: selected {len(basis)} vectors but rank is {rank_k}")

    basis_by_k[k] = basis
    coeff_by_k[k] = C
    if basis:
        cache_pm = pf.ExpressionManager(ctx, resolve_parameters=dict(params_sp))
        coeff_inputs[k] = {
            "context": ctx, "expression": lyap[k],
            "parameters": dict(params_sp), "tolerances": dict(search_tolerances),
            "basis_ids": tuple(id(v) for v in basis),
            "basis_coords": np.column_stack([
                cache_pm.eval_vector(v).coords for v in basis
            ]).astype(float).copy(),
            "target_coords": cache_pm.eval_scalar(lyap[k]).inner_prod_coords.astype(float).copy(),
        }
    labels = [str(v) for v in basis]
    zeros = int(np.sum(np.abs(C) < search_tolerances["zero_tol"])) if C.size else 0
    print(f"  sparse basis: {labels}")
    print(f"  zero coefficients: {zeros}/{C.size}")
```

Interpret the result in two layers:

1. `spanning_by_k[k]` is the full list of candidate vectors that lie in `col(V_k)`.
2. `basis_by_k[k]` is one selected basis: it has `rank(V_k)` independent vectors and gives a sparse symmetric decomposition of the quadratic part of `V_k`.

Look for a **k-dependent pattern** on the retained interior in `basis_by_k`, not only in the larger column-space list. Document separate patterns for `exceptional_indices`; they remain part of the potential and its proof. Common patterns:
- `[x_0 − x_star, grad_f(x_k), x_{k+1} − x_star]` (GD-like, 3 vectors)
- `[A(x_N), y_0 − x_N]` (APPM-like, 2 constant vectors)
- Pattern with `x_{k+1}` shifting as k increases

**Check linear independence**: Make sure to check that the vectors corresponding to the conjectured pattern are linearly independent. Otherwise, the proposed set is degenerate. If the sparse basis is awkward but another independent subset gives a clearer algorithmic pattern, it is acceptable to use the clearer subset, but record the reason and verify its decomposition residual in Step 4.

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

**Basis recovery**: If no consistent reconstructing basis pattern is identified on the retained interior, or the candidates do not span the required ranks, retain the spanning sets, sparse bases, zero-counts, and failed reconstruction evidence for the actual searched indices in `supplementary/`. Consider meaningful auxiliary sequences, then return to Block 3's authorized structural/horizon recovery within the same attempt and remaining budget. Follow Block 3's ceiling and approval rules; do not turn this recoverable failure directly into a request for human mathematical guidance. If its selected certificate, grouping, or horizon changes, reload that coherent handoff and rebuild the partial sums and basis data.

Do not proceed to coefficient extraction until a consistent basis hypothesis is identified. Every exceptional index also needs a valid basis or a verified rank-zero quadratic part; excluding it from the rank comparison does not remove any expression or proof term.

---

## Step 4 — Extract Coefficient Matrices

For each required k, compute the symmetric matrix `C[k]` for the quadratic part, `sum_{i,j} C[i,j] * <v_i, v_j>`. Off-diagonal entries therefore contribute twice. Retain function-value and scalar-offset terms separately; a quadratic reconstruction alone does not describe the whole potential.

Reuse the search result only for unchanged inputs and a successful fresh reconstruction check. Otherwise, extract coefficients again with the existing utility and its original tolerances. Keep the notebook coefficient displays and formula checks below. Include every index from 0 through N, including all documented boundary exceptions: use a separate basis template when the interior one does not apply, and retain all applicable function-value/constant components. If a nonzero exceptional index needs an additional basis search, perform and display the same real search and independence checks there. Rank-zero quadratic parts use an empty basis and a 0-by-0 matrix, without discarding their function-value terms.

```python
# (continuing — lyap, basis_by_k, ctx, params_sp available)
import fractions

def V_k_basis(k):
    # Use basis_by_k[k], or replace this with the manually identified pattern from Step 3:
    # Example (GD-like):
    #   return [ctx["x_0"] - ctx["x_star"], obj.grad(ctx[f"x_{k}"]), ctx[f"x_{k+1}"] - ctx["x_star"]]
    return basis_by_k.get(k, [])

# Preserve the extraction utility's original defaults independently of search settings.
extraction_tolerances = dict(indep_tol=1e-7, span_tol=1e-5)
coefficient_pm = pf.ExpressionManager(ctx, resolve_parameters=dict(params_sp))
cached_coefficients = coeff_by_k
coeff_by_k = {}  # Rebuild output so failed/omitted indices cannot retain old C.
coefficient_residuals = {}
required_indices = list(range(N_int + 1))
for k in required_indices:
    cached_C = cached_coefficients.get(k)
    basis = V_k_basis(k)
    if not basis:
        target = coefficient_pm.eval_scalar(lyap[k]).inner_prod_coords.astype(float)
        if np.linalg.matrix_rank(target, tol=b3.get("rank_tolerance", 1e-4)) != 0:
            raise ValueError(f"k={k}: nonzero quadratic part has no verified basis")
        residual = float(np.linalg.norm(target, ord="fro"))
        if residual > extraction_tolerances["span_tol"] * max(1.0, np.linalg.norm(target, ord="fro")):
            raise ValueError(f"k={k}: empty-basis reconstruction fails")
        coeff_by_k[k] = np.zeros((0, 0))
        coefficient_residuals[k] = residual
        print(f"k={k}: rank-zero quadratic part; retain function/offset terms")
        continue
    try:
        matrix = np.column_stack([
            coefficient_pm.eval_vector(v).coords for v in basis
        ]).astype(float)
        target = coefficient_pm.eval_scalar(lyap[k]).inner_prod_coords.astype(float)
        basis_rank = int(np.linalg.matrix_rank(matrix, tol=extraction_tolerances["indep_tol"]))
        if basis_rank != len(basis) or len(basis) != ranks[k]:
            raise ValueError(f"k={k}: basis is not independent and rank-spanning")
        previous = coeff_inputs.get(k)
        unchanged = (
            previous is not None
            and previous["context"] is ctx and previous["expression"] is lyap[k]
            and previous["parameters"] == params_sp
            and previous["tolerances"] == search_tolerances
            and all(previous["tolerances"][key] == value
                    for key, value in extraction_tolerances.items())
            and previous["basis_ids"] == tuple(id(v) for v in basis)
            and np.array_equal(previous["basis_coords"], matrix)
            and np.array_equal(previous["target_coords"], target)
        )
        reusable = (
            unchanged and cached_C is not None
            and cached_C.shape == (len(basis), len(basis))
            and np.all(np.isfinite(cached_C))
            and np.array_equal(cached_C, cached_C.T)
            and np.linalg.norm(matrix @ cached_C @ matrix.T - target, ord="fro")
                <= extraction_tolerances["span_tol"] * max(1.0, np.linalg.norm(target, ord="fro"))
        )
        if reusable:
            C = cached_C
        else:
            C = find_symmetric_coefficient_matrix(
                lyap[k], basis, pep_context=ctx, resolve_parameters=params_sp,
                **extraction_tolerances)
        if C.shape != (len(basis), len(basis)) or not np.all(np.isfinite(C)):
            raise ValueError(f"k={k}: invalid coefficient matrix")
        if not np.array_equal(C, C.T):
            raise ValueError(f"k={k}: coefficient matrix must be symmetric")
        residual = float(np.linalg.norm(matrix @ C @ matrix.T - target, ord="fro"))
        if residual > extraction_tolerances["span_tol"] * max(1.0, np.linalg.norm(target, ord="fro")):
            raise ValueError(f"k={k}: coefficient reconstruction failed: {residual}")
        coeff_by_k[k] = C
        coefficient_residuals[k] = residual
        labels = [str(v) for v in basis]
        print(f"k={k}:")
        for i in range(C.shape[0]):
            for j in range(i, C.shape[1]):
                if abs(C[i,j]) > 1e-6:
                    frac = fractions.Fraction(float(C[i,j])).limit_denominator(1000)
                    print(f"  C[{labels[i]}, {labels[j]}] = {C[i,j]:.6f}  ≈  {frac}")
    except ValueError as e:
        raise ValueError(f"k={k}: basis/coefficient reconstruction is unresolved") from e

assert set(coeff_by_k) == set(required_indices)
```

---

## Step 5 - Optional Coefficient Fitting and Expression Structure

The Block 4 gate is an interpretable basis pattern with successful independence and numerical reconstruction checks. A fitted coefficient formula is optional. Block 2's initial lambda/S closed-form attempt remains required there; do not require another search or a user checkpoint here solely because coefficient formulas remain unresolved.

```python
# Set these before optional fitting; replace them with actual checked source
# and its status if a usable formula is available.
coeff_code = None
coefficient_formula_status = "unresolved"
```

When a fit is useful, inspect the printed fractions for possible dependence on `k` and `N`:
- Constant: `C[i,j] = c`
- Linear: `C[i,j] = a*k + b`
- Quadratic: `C[i,j] = a*k**2 + b*k + c`
- A reciprocal with a simple polynomial pattern

Reuse applicable known formulas and test candidate `coeff_pattern(k, N)` values against every available numerical matrix at its own horizon and parameter values, with the original tolerances. Do not treat one fixed-N sample as evidence for all horizons. Record a fit's actual numerical check results; numerical agreement does not establish an analytic identity or signs.

If fitting is skipped or unsuccessful, set `coeff_code` to null and pass named unknown functions such as `c_00(k, N)` and `c_01(k, N)` for the unresolved entries. Never substitute zeros or a function returning an empty dictionary for unknown formulas. Retain any useful partial formulas or rejected candidates with their status and residuals.

Describe the full expression structure for Block 5: the ordered basis for each interior/initial/terminal case; the symmetric quadratic convention; meaningful function-value expressions such as `f(x_k)-f_star` with known or unknown coefficient functions; and constant or cumulative terms where present. Use distinct coefficient functions for exceptional cases when the same formula has not been established. Keep the numerical function-coordinate arrays, their labels, and offsets as evidence, and show how the proposed expression terms reproduce them. If the expression structure itself is not identified, continue structural diagnosis; deferring a formula does not excuse missing basis, component, or boundary data.

Use `coefficient_formula_status` = `unresolved` when a complete usable formula is unavailable, `candidate` for a formula checked only against numerical samples, or `verified` only with documented analytic justification for the formula's stated domain. This status does not establish a full-PEP or Lyapunov proof. Keep existing applicable analytic formulas without rediscovering them.

Block 5 derives unresolved Lyapunov coefficients jointly with required local interpolation/square multipliers from the actual recurrence, step identity, initial/terminal conditions, and target normalization. Continue there once the numerical structure checks pass, even when `coeff_code` is null. Return to the basis recovery above when no suitable spanning pattern or valid reconstruction has been found; unresolved formulas alone do not trigger recovery.

---

## Step 6 - Save the Numerical Structure and Analytic Unknowns

Capture `basis_code` from the actual finalized executable basis definitions, including labels and index conventions. It must reconstruct the interior and exceptional basis patterns in a fresh setup context; referencing an earlier process's `basis_by_k` dictionary is not a reusable definition. Preserve the existing coefficient-cache guards and the successful numerical checks. Use `coeff_code = None` when executable coefficient source is unavailable; preserve known formulas in `expression_structure` and retain the exact tested source when available. Record `coefficient_formula_status` from the mathematical evidence, independently of whether that source field is populated.

Use the following structure consistently in `expression_structure`:

- `quadratic_convention`: state `V_quadratic = sum_{i,j} C_ij * <v_i, v_j>`, with symmetric C and off-diagonal entries counted twice.
- `interior`, `initial`, and `terminal`: each describes its `index_domain`, ordered `basis_labels`, and the known formula or named unknown function for each independent quadratic coefficient. Use the recorded interior domain `a <= k <= N-b`; describe excluded left indices under `initial` and excluded right indices under `terminal`, with separate indexed subcases when needed. Record the actual values of a and b in these descriptions. A case may be empty when that end has no exclusions, but V_0 and V_N still require reconstruction in their applicable case. An empty quadratic basis is valid when its actual quadratic rank is zero. State exceptional small-horizon formulas separately inside the applicable case.
- `function_terms`: actual meaningful function-value or cumulative expressions, their case/index domains, and known or named unknown coefficients. An empty list means verified absence of these terms, not an unresolved reconstruction.
- `constant_terms`: the corresponding scalar-offset expressions and coefficients, or an empty list only when absent.

`unresolved_coefficients` is a list of records `{name, arguments, role, index_domain}`. For example, a still-unknown interior off-diagonal entry may be recorded as `{"name": "c_01", "arguments": ["k", "N"], "role": "interior.C[0,1] = interior.C[1,0]", "index_domain": "a <= k <= N-b"}`. Include algorithm parameters in `arguments` where they remain symbolic. Name function-value/constant coefficients and distinct initial/terminal unknowns as well; the expression structure must unambiguously map each unknown to its term. Available partial formulas remain in the relevant case even if other entries are unresolved.

Before saving, construct the executed `V_k_structure(k)` from the inferred basis, the numerical C at that sample, and the identified function-value/constant terms with their numerical sample coefficients. It must visibly assemble those terms, rather than return `lyap[k]` or copy its coordinates. Capture its actual executed source as `structure_code`, including any function/offset sample-coefficient dictionaries it needs beyond `ctx`, `params_sp`, `N_int`, the basis definitions, and `coeff_by_k`. Replay that same source before checking the complete expression against every required partial sum. This source reconstructs numerical samples; it must not solve, launch another basis search, or pretend the sample values are all-horizon formulas. This verifies the observed structure without claiming the unknown coefficient functions are known for other horizons.

```python
# basis_code, structure_code, templates, expression_structure, unresolved_coefficients,
# coeff_code (possibly None), and coefficient_formula_status are the actual
# sources/descriptions finalized above; do not replace them with dummy formulas.
assert isinstance(basis_code, str) and basis_code.strip()
assert isinstance(structure_code, str) and structure_code.strip()
assert coefficient_formula_status in {"unresolved", "candidate", "verified"}
if coeff_code is not None:
    assert isinstance(coeff_code, str) and coeff_code.strip()
if coefficient_formula_status == "unresolved":
    assert unresolved_coefficients, "Name every unresolved coefficient explicitly"
assert set(expression_structure) == {
    "quadratic_convention", "interior", "initial", "terminal",
    "function_terms", "constant_terms",
}
for unknown in unresolved_coefficients:
    assert set(unknown) == {"name", "arguments", "role", "index_domain"}
    assert unknown["name"] and unknown["arguments"] and unknown["role"]
assert certificate_checked and grouping_checked
assert set(coeff_by_k) == set(required_indices)

exec(compile(structure_code, "<Block-4-numerical-structure>", "exec"), globals())
component_residuals = {}
for k in required_indices:
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for name, residual, target_component in (
        ("gram", diff.inner_prod_coords, target.inner_prod_coords),
        ("function", diff.func_coords, target.func_coords),
        ("offset", diff.offset, target.offset),
    ):
        residual = np.asarray(residual, dtype=float)
        target_component = np.asarray(target_component, dtype=float)
        error = float(np.max(np.abs(residual))) if residual.size else 0.0
        scale = float(np.max(np.abs(target_component))) if target_component.size else 0.0
        assert np.all(np.isfinite(residual))
        assert error <= reconstruction_tolerance + reconstruction_rtol * scale, (k, name, error)
        component_residuals[str(k)][name] = error

numerical_reconstruction = {
    "certificate_id": b3["certificate_id"],
    "required_indices": required_indices,
    "quadratic_residuals": {str(k): value for k, value in coefficient_residuals.items()},
    "component_residuals": component_residuals,
    "tolerances": {
        **extraction_tolerances,
        "component_atol": reconstruction_tolerance,
        "component_rtol": reconstruction_rtol,
    },
    "passed": True,  # Set only after every actual reconstruction check above.
}
state = {
    **b3,  # Keep the complete same-certificate snapshot and its ID-covered fields.
    "numerical_certificate_verified": True,  # Rechecked above, not inferred from a flag.
    "analytic_full_pep_verified": b3.get("analytic_full_pep_verified", False),
    "lyapunov_proof_verified": False,  # Block 5 must establish the analytic proof.
    "basis_templates": templates,
    "basis_code": basis_code,
    "structure_code": structure_code,
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": coeff_code,
    "coefficient_formula_status": coefficient_formula_status,
    "expression_structure": expression_structure,
    "unresolved_coefficients": unresolved_coefficients,
    "numerical_reconstruction": numerical_reconstruction,
}
state_path = state_dir / "{ALGO_NAME}_b4.json"
state_path.write_text(json.dumps(state, indent=2, allow_nan=False), encoding="utf-8")
print("State saved to", state_path)
```

Do not reload an earlier b3 file over the verified in-memory certificate before saving. Preserve `named_dual_values`, `constraint_metadata`, `numerical_decomposition`, `certificate_provenance`, `numerical_checks`, `normalization`, coordinate labels, and every other certificate-ID input unchanged. New basis/structure fields and nullable formula source are additive; they are not part of the certificate fingerprint. Retain Block 2's initial-search record and unresolved lambda/S candidates, together with Block 3's `rank_search` and its supplementary evidence. Do not relabel another horizon's evidence as this selected certificate.

For an existing analytic-path state, retain its usable `basis_code` and `coeff_code`, derive the matching expression description and `structure_code` from the actual earlier mathematical cells, and rerun the same numerical basis/component checks. A legacy `proof_valid` flag or a numerically fitted coefficient formula never promotes either analytic proof status. Failed rank, basis, full-component reconstruction, or certificate checks still block progression; unresolved analytic coefficients alone do not.

---

## Step 7 — Update Lyapunov Notebook

Open the existing notebook and add or replace the special-vector and coefficient sections with this structure:

1. `## Identify the vectors composing the Lyapunov function`
   - A short markdown cell explaining that Block 4 starts from the Block 3 partial sums and searches for interpretable rank-spanning vectors.
   - A code cell that rebuilds or sanity-checks the selected rank profile against Block 3, with the recorded interior domain, explicit boundary exceptions, and a concise reference to its cross-horizon comparison when present.
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
   - A visible, executable code cell that calls `find_basis_with_sparsest_coefficients(...)` on the actual `lyap[k]` and filtered column-space candidates, using the context, parameter values, tolerances, and any `fixed_vectors` used in Step 3. Retain its executed notebook output for every searched `k`: the index and rank, selected basis labels (`sparse basis: [...]`), and near-zero coefficient count and total (`zero coefficients: n/m`, using the actual `zero_tol`).
   - Candidate filtering or a final basis definition alone does not show the search. Keep the actual search call visible in this cell; a saved-state summary, hard-coded selected basis, or helper-only replay does not satisfy this requirement. Within a notebook run, reuse the search results under the existing coefficient-reuse conditions rather than rerunning the search solely to format its output.
   - If a clearer independent basis is adopted instead of the search-selected basis, show both choices, explain the reason, and include the adopted basis's decomposition-residual check.
   - A markdown cell stating the inferred rank-spanning template as a displayed formula, including any special terminal/boundary case.
   - A code cell defining `V_k_basis(k)` and `V_k_basis_labels(k)`, then printing the independence check in the compact form:
     ```
     k=1: rank r basis [...]
     ```
4. `### Coefficient matrices`
   - A markdown cell stating the basis order used for interior and terminal cases.
   - A code cell decomposing every required `V_k`, printing the actual reconstruction residual per `k`, and displaying each numerical coefficient matrix with `pf.pprint_labeled_matrix`. Include the function-value coordinates with meaningful labels and any scalar offset, including initial and terminal cases.
   - When a coefficient fit is available, define `coeff_pattern(k, N)`, show its comparison matrices, and print its actual formula residuals. Otherwise display the named unknown coefficient functions and their basis/function/constant terms; do not fabricate a formula check or a zero-returning `coeff_pattern`.
5. `### Block 4 conclusion`
   - A markdown cell stating the full `V_k` expression structure, using available formulas and explicit unknown coefficient functions, with the interior and exceptional cases. Distinguish numerical reconstruction from an analytic proof and state that Block 5 derives any remaining coefficients and verifies the step, base, and boundary identities.

When displaying coefficient matrices in the notebook, use `pf.pprint_labeled_matrix(C, basis_labels, basis_labels, ...)` or an equivalent labeled matrix display. Avoid manual nested-loop row prints such as `print(["1/2", "-1/4"])`; those are hard for users to scan and detach coefficients from their basis vectors.

Do not expose the JSON persistence step for `{ALGO_NAME}_b4.json` as notebook content. The notebook should show the basis discovery, coefficient matrices, full expression structure, and any available coefficient formulas; writing the state file is command/workflow machinery and should happen outside the notebook, or inside a helper invoked by the command script. Avoid even a visible `save_block4_state(...)` notebook cell unless the save operation itself is part of the user's reasoning task.

Do not defer these cells to Block 5; Block 5 should refine and verify them, not create the whole diagnostic trail for the first time.

For notebook Markdown cells added or edited in this block, use `$...$` for inline math and `$$...$$` for display math. Verify their rendered appearance, not just their source delimiters, and record any unresolved rendering issue in the supplementary checklist.

If a separate file is created or reused to justify a proof condition in this block, include its relevant identity definitions, actual checks/results, and reasoning in the notebook under the [proof verification rule](../../plugins/pepflow-workflows/references/output-layout.md#proof-verification-files-during-notebook-authoring). Reuse existing cells. Preserve the numerical handoff and explicit unresolved analytic status; this adds no earlier analytic-proof prerequisite.

Update the notebook's sibling `supplementary/<notebook-stem>_checklist.md` with this block's actual cell references, evidence, and unresolved requirements, following Block 1's Notebook Lifecycle. Inspect every notebook requirement listed above; future-block work stays pending. Keep the record out of the notebook and routine completion report, and disclose any unresolved requirement due in this block.

---

## Output

Report:
- The basis template for V_k (k-indexed pattern of special vectors)
- The coefficient matrix `C[k]` for each k (as a table of fractions)
- The available coefficient formulas or named unknown functions for Block 5, including nonquadratic and exceptional-case terms
- Numerical reconstruction results and the separate numerical-certificate, analytic full-PEP, and analytic Lyapunov verification statuses

- Confirmation that the notebook was updated through the vector/coefficient sections

**Next step**: `/lyap-closed-form {ALGO_NAME}`
