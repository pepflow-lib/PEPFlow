# /lyap-define: PEPFlow Block 3 — Defining the Lyapunov Function

Using the Full-PEP dual certificates from Block 2, build partial-sum sequences V_k by accumulating weighted inequalities step by step, and investigate a consistent low rank across iterations and horizons with fixed boundary exceptions.

> $ARGUMENTS  (ALGO_NAME, e.g. `heavy_ball`)

---

## Environment

PEPFlow repo root: `$(git rev-parse --show-toplevel)/`
Python executable: `.venv/bin/python3`
Input: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json`
Output: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json`
Notebook: update `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb`

## Output Layout

Before creating files, read and follow [the shared output layout](../../../references/output-layout.md). Resolve the example paths below from the actual output notebook directory, including when it is under `examples_peppy/`.

---

## Reference Scope

When looking for reference examples, notebook structure, proof-writing patterns, or prompt skeletons, use only files under `examples_peppy/`. The `examples_peppy/_references/` subtree is explicitly allowed and may be used freely as reference material. Do not inspect or follow other repository example/reference files outside `examples_peppy/` for this workflow.

---

## Step 1 — Load State and Recreate Context

Run the Python fragments in this block in order in one process or notebook kernel from the repository root. Rebuild the setup without solving: all numerical lambda blocks, S, and scalar/PSD extras below belong to the saved Block 2 certificate.

The default Block 2 handoff requires a meaningful initial closed-form attempt, not success. Do not repeat that search here or stop only because `lamb_code` or `S_code` is null. Require a checked numerical certificate and the recorded initial attempt; preserve the separate analytic statuses. If the user explicitly requested an analytic full-PEP proof, keep that outstanding objective visible.

For a legacy state missing the complete certificate, recover its matching data, executed source, and evidence from the existing notebook/state. A legacy `proof_valid` flag alone establishes neither certificate completeness nor an all-parameter proof. If recovery requires a new solve, return to Block 2 and replace lambda, S, extras, bound, provenance, and checks together; retain usable formulas with their actual verification status. Never fill missing extras with zero or mix saved lambda with a fresh S.

```python
import pepflow as pf, numpy as np, sympy as sp, importlib.util, json, itertools
from pathlib import Path

REPO_ROOT = Path.cwd().resolve()
with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json", encoding="utf-8") as fh:
    b2 = json.load(fh)
certificate = b2
if not certificate.get("numerical_certificate_verified", False):
    raise ValueError("Recover or verify the complete numerical certificate in Block 2")
if not certificate.get("closed_form_search", {}).get("completed", False):
    raise ValueError("Complete or recover Block 2's initial closed-form attempt")

N_int = certificate["N_verify"]
N = sp.S(N_int)
params = json.loads(certificate["params_json"])
params_sp = {
    name: (sp.Rational(value) if isinstance(value, str) else
           sp.nsimplify(value, rational=True, tolerance=1e-9)
           if isinstance(value, float) else sp.S(value))
    for name, value in params.items()
}
spec = importlib.util.spec_from_file_location("setup",
    "examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py")
if spec is None or spec.loader is None:
    raise ImportError("Cannot load the selected setup")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ctx, pb, obj = mod.get_pep_setup(N, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
ctx.set_as_current()
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
```

The following check is mathematical reconstruction from saved numbers, not restoration of a solver object. Capture its actual executed source as `certificate_check_code` for Block 4. It consumes `certificate`, `REPO_ROOT`, `N_int`, `params_sp`, `ctx`, `pb`, and `obj`, and must recompute `certificate_checked`; no stored boolean substitutes for its checks.

---

## Step 2 — Extract All Dual Variables

Collect every initial constraint and every function/operator interpolation group from the rebuilt setup. Check the saved certificate identity, source, coordinate order, constraint metadata, scalar/PSD duals, and numerical S decomposition before grouping. These checks establish consistency only for this horizon and parameter sample.

```python
import hashlib
import json
from pathlib import Path
import numpy as np
import sympy as sp
import pepflow as pf
from pepflow.constraint import ScalarConstraint, PSDConstraint
from pepflow.operator import LinearOperatorTranspose
from pepflow.pep_result import MatrixWithNames
from pepflow.utils import name_to_vector_tuple

certificate_checked = False
if not certificate.get("numerical_certificate_verified", False):
    raise ValueError("Recover or verify the complete numerical certificate in Block 2")
if not certificate.get("closed_form_search", {}).get("completed", False):
    raise ValueError("Complete or recover Block 2's initial closed-form attempt")
certificate_keys = (
    "N_verify", "params_json", "relaxed_constraints",
    "S_matrix", "S_row_names", "S_col_names", "basis_vectors", "basis_scalars",
    "opt_value", "tau_sol", "tau_name", "named_dual_values", "constraint_metadata",
    "normalization", "certificate_provenance", "numerical_checks",
    "numerical_decomposition",
)
payload = {key: certificate[key] for key in certificate_keys}
digest = hashlib.sha256(json.dumps(
    payload, sort_keys=True, separators=(",", ":"), allow_nan=False
).encode("utf-8")).hexdigest()
if digest != certificate["certificate_id"]:
    raise ValueError("Certificate components changed; recover one coherent certificate")
provenance = certificate["certificate_provenance"]
if provenance["pep_type"] != "primal":
    raise ValueError("Recover and verify the certificate's actual dual sign convention")
for relative_path, expected_hash in provenance["source_hashes"].items():
    source_path = (REPO_ROOT / relative_path).resolve()
    if not source_path.is_relative_to(REPO_ROOT):
        raise ValueError("Certificate source path must stay in the selected repository")
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != expected_hash:
        raise ValueError(f"Certificate source changed: {relative_path}")
if not Path(pf.__file__).resolve().is_relative_to(REPO_ROOT):
    raise ValueError("The imported PEPFlow source is not the selected repository")
if N_int != certificate["N_verify"]:
    raise ValueError("Certificate horizon differs from the rebuilt setup")
saved_params = json.loads(certificate["params_json"])
expected_params = {
    key: (sp.Rational(value) if isinstance(value, str) else
          sp.nsimplify(value, rational=True, tolerance=1e-9)
          if isinstance(value, float) else sp.S(value))
    for key, value in saved_params.items()
}
if params_sp != expected_params:
    raise ValueError("Certificate parameters differ from the rebuilt setup")
if not certificate["numerical_checks"]["passed"]:
    raise ValueError("Block 2 numerical checks did not pass")
tol = certificate["numerical_checks"]["tolerances"]

records = [(c, "initial", None, None) for c in pb.init_conditions]
owners = list(ctx.func_to_triplets) + [
    owner for owner in ctx.oper_to_duplets
    if not isinstance(owner, LinearOperatorTranspose)
]
for owner in owners:
    data = ctx.get_constraint_data(owner)
    for group, family in data.sc_dict.items():
        records.extend((c, "interpolation", str(owner), str(group)) for c in family)
    records.extend((c, "interpolation", str(owner), str(group))
                   for group, c in data.psd_dict.items())
constraints_by_name = {c.name: c for c, _, _, _ in records}
if len(constraints_by_name) != len(records):
    raise ValueError("Constraint names must identify one unique contribution")
saved_meta = certificate["constraint_metadata"]
saved_duals = certificate["named_dual_values"]
if set(constraints_by_name) != set(saved_meta) or set(saved_duals) != set(saved_meta):
    raise ValueError("The saved certificate does not cover the rebuilt constraints")
relaxed = set(certificate["relaxed_constraints"])
if set(pb.relaxed_constraints) != relaxed or not relaxed.issubset(constraints_by_name):
    raise ValueError("The selected relaxation differs from the saved certificate")
if pb.ctx is not ctx:
    raise ValueError("The builder and expression context differ")
basis = list(ctx.basis_vectors())
basis_labels = [repr(v) for v in basis]
scalar_labels = [repr(v) for v in ctx.basis_scalars()]
if basis_labels != certificate["basis_vectors"] or scalar_labels != certificate["basis_scalars"]:
    raise ValueError("Certificate coordinate order differs from the rebuilt context")
if certificate["S_row_names"] != basis_labels or certificate["S_col_names"] != basis_labels:
    raise ValueError("S labels do not match the rebuilt basis")
S_array = np.asarray(certificate["S_matrix"], dtype=float)
if S_array.shape != (len(basis), len(basis)) or not np.all(np.isfinite(S_array)):
    raise ValueError("Invalid S shape or entries")
if not np.allclose(S_array, S_array.T, atol=tol["psd_tol"], rtol=0):
    raise ValueError("S is not numerically symmetric")
if len(basis) and np.linalg.eigvalsh((S_array + S_array.T) / 2).min() < -tol["psd_tol"]:
    raise ValueError("S failed the recorded PSD tolerance")
S_sol = MatrixWithNames(S_array, basis_labels, basis_labels)
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
S_scalar = sum((float(S_array[i, j]) * basis[i] * basis[j]
                for i, j in np.ndindex(S_array.shape)), pf.Scalar.zero())

weighted_terms = {}
interpolation_terms = {}
interpolation_pairs = {}
extra_terms = {}
extra_duals = {}
for constraint, origin, owner, group in records:
    name = constraint.name
    kind = "scalar" if isinstance(constraint, ScalarConstraint) else "psd"
    residual = constraint.lhs - constraint.rhs
    shape = [] if kind == "scalar" else list(np.shape(residual))
    expected_meta = dict(origin=origin, owner=owner, group=group, kind=kind,
                         comparator=constraint.cmp.value, shape=shape,
                         relaxed=name in relaxed)
    if any(saved_meta[name].get(key) != value for key, value in expected_meta.items()):
        raise ValueError(f"Constraint metadata changed: {name}")
    value = saved_duals[name]
    if name in relaxed:
        if value is not None:
            raise ValueError(f"A relaxed constraint must have no retained multiplier: {name}")
        continue
    if value is None:
        raise ValueError(f"Missing unrelaxed dual: {name}")
    dual = np.asarray(value, dtype=float)
    if list(dual.shape) != shape or not np.all(np.isfinite(dual)):
        raise ValueError(f"Invalid saved dual: {name}")
    # Normalize inequalities to residual <= 0; primal equality duals keep their sign.
    if constraint.cmp.name in ("GE", "SEQ"):
        residual = -residual
    if kind == "scalar":
        if constraint.cmp.name != "EQ" and float(dual) < -tol["dual_tol"]:
            raise ValueError(f"Negative inequality multiplier: {name}")
        contribution = pf.Scalar.zero() + float(dual) * residual
    else:
        if constraint.cmp.name != "EQ" and not np.allclose(dual, dual.T, atol=tol["psd_tol"], rtol=0):
            raise ValueError(f"Nonsymmetric matrix dual: {name}")
        if constraint.cmp.name != "EQ" and dual.size and np.linalg.eigvalsh((dual + dual.T) / 2).min() < -tol["psd_tol"]:
            raise ValueError(f"Matrix dual is not PSD: {name}")
        contribution = sum((float(dual[i, j]) * residual[j, i]
                            for i, j in np.ndindex(dual.shape)), pf.Scalar.zero())
    weighted_terms[name] = contribution
    if origin == "interpolation" and kind == "scalar":
        interpolation_terms[name] = contribution
        try:
            interpolation_pairs[name] = name_to_vector_tuple(name)
        except (ValueError, IndexError):
            interpolation_pairs[name] = None  # Assign this term explicitly when grouping.
    elif name != certificate["tau_name"]:
        extra_terms[name] = contribution
        extra_duals[name] = value

tau_name = certificate["tau_name"]
if (tau_name not in weighted_terms or saved_meta[tau_name]["origin"] != "initial"
        or saved_meta[tau_name]["kind"] != "scalar" or tau_name in relaxed
        or certificate["normalization"]["tau_name"] != tau_name):
    raise ValueError("Missing or inconsistent bound normalization constraint")
if not np.allclose(saved_duals[tau_name], certificate["tau_sol"], atol=tol["dual_tol"], rtol=0):
    raise ValueError("The saved normalization dual is inconsistent")
if not np.isfinite(certificate["opt_value"]) or not np.allclose(
    certificate["normalization"]["bound_value"], certificate["opt_value"],
    atol=tol["identity_atol"], rtol=tol["identity_rtol"]
):
    raise ValueError("The saved bound/normalization is inconsistent")
certificate_diff = (pb.performance_metric - float(certificate["opt_value"])
                    - sum(weighted_terms.values(), pf.Scalar.zero()) + S_scalar)
evaluated_diff = pm.eval_scalar(certificate_diff)
for label, coords in (
    ("Gram", evaluated_diff.inner_prod_coords),
    ("function", evaluated_diff.func_coords),
    ("offset", np.asarray(evaluated_diff.offset)),
):
    if not np.allclose(np.asarray(coords, dtype=float), 0,
                       atol=tol["identity_atol"], rtol=tol["identity_rtol"]):
        raise ValueError(f"Numerical certificate {label} identity failed")
decomposition = certificate["numerical_decomposition"]
D_saved = np.asarray(decomposition["D"], dtype=float)
E_saved = np.asarray(decomposition["ell_coords"], dtype=float)
if decomposition["basis_labels"] != basis_labels or E_saved.ndim != 2:
    raise ValueError("Numerical S decomposition basis differs")
if E_saved.shape[1] != len(basis) or D_saved.shape != (E_saved.shape[0], E_saved.shape[0]):
    raise ValueError("Numerical S decomposition shape differs")
if not np.all(np.isfinite(D_saved)) or not np.all(np.isfinite(E_saved)):
    raise ValueError("Numerical S decomposition contains nonfinite values")
if not np.allclose(E_saved.T @ D_saved @ E_saved, S_array,
                   atol=tol["reconstruction_atol"], rtol=tol["reconstruction_rtol"]):
    raise ValueError("Numerical S decomposition does not reconstruct this certificate")
certificate_checked = True
print("Numerical certificate checked for this N and parameter sample.")
```

Keep every interpolation family, including different functions/operators, and every scalar/PSD extra. The matrix pairing is `trace(dual @ residual)`, not a scalar multiplier or part of the Gram S. Retain raw below-threshold values; a display cutoff does not authorize omitting their weighted residual from the identity or coverage.

The normalized equality convention above is for the captured primal result. Recover another solver formulation coherently in Block 2 with its verified sign convention rather than changing one multiplier locally. Compare the recorded solver settings and descriptive normalization to the intended experiment as well. A successful fixed-sample numerical check does not set `analytic_full_pep_verified` or `lyapunov_proof_verified`.

---

## Step 3 - Choose the S Decomposition


Closed-form success is not required here. The initial search belongs to Block 2; use its checked numerical decomposition when formulas remain unresolved. A stored candidate or reference must match this same saved S before being used, and numerical agreement must retain its numerical status.

Before computing a new numerical LDL decomposition, check whether Block 2 or
`examples_peppy/_references/{ALGO_NAME}/` already gives a verified closed-form
or direct decomposition of the Gram dual certificate `S`. If a known
decomposition exists, try it first. Do not replace a useful proof-specific
decomposition with a generic LDL factorization just because LDL is available.
If its partial sums do not give a useful rank pattern, Step 5 permits other
verified decompositions of this same S.

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

Try the applicable known decomposition before computing fresh factors. If none
is available, or its partial sums fail the rank diagnosis, record that finding
and try another verified decomposition under Step 5. Evaluation clean-room
restrictions still control which references may be read. Keep alternative
factorizations as separate trials of the same certificate; verify reconstruction
and signs without replacing unrelated certificate components.

```python
# (continuing from the checked saved certificate above)
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

# Reuse Block 2's checked numerical factors; no second factorization or solve.
D = np.asarray(certificate["numerical_decomposition"]["D"], dtype=float)
E = np.asarray(certificate["numerical_decomposition"]["ell_coords"], dtype=float)
ell = [sum((float(coef) * vector for coef, vector in zip(row, basis)),
           pf.Vector.zero()) for row in E]
# For a fresh trial, compute numerical reverse LDL of this SAME saved S.
# Verify reconstruction and signs, and record the trial separately without
# changing the original certificate components:
# D, ell = ldl_decompose_with_reversed_basis(S_sol, basis, print_output=False)

n = D.shape[0]
print("D diagonal:", [round(float(D[i, i]), 6) for i in range(n)])
print("ell vectors:", [str(e) for e in ell])
# LDL permutations change factor order; match D and ell indices.
S_piece_terms = {}
a = 0
while a < n:
    block = [a]
    if a + 1 < n and (D[a, a + 1] != 0 or D[a + 1, a] != 0):
        block.append(a + 1)
    outside = [j for j in range(n) if j not in block]
    if np.any(D[np.ix_(block, outside)] != 0) or np.any(D[np.ix_(outside, block)] != 0):
        raise ValueError("Adapt S pieces to retain every off-diagonal block")
    S_piece_terms[a] = sum((float(D[i, j]) * ell[i] * ell[j]
                           for i in block for j in block), pf.Scalar.zero())
    a += len(block)
```

For cases where `S` is a single squared term or a known sum of squared terms,
try the known terms first; compute alternatives only under Step 5 recovery.

Record the selected decomposition as executed `decomposition_code`, including the complete `S_piece_terms` representation and its reconstruction check against the saved S. Prefer applicable known direct/per-step expressions; record why any alternative is tried under Step 5. For numerical LDL, pair `D[a,b]` with `ell[a] * ell[b]`, retain off-diagonal blocks, and determine factor-to-step assignments from the actual expressions. A missing closed form never requires another analytic search in this block.

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

- **Smooth function problems**:
  - As the basic rule, at step `j`, include all inequalities involving `star` up to iterate `j+1`, and include all consecutive inequalities up to iterate `j`, without omission.
  - First add the initial boundary interpolation term `(star, 0)` outside the loop.
  - At step `j`, add the new terms: `(star, j+1)` and the consecutive inequalities whose larger index is `j+1`.

- **Operator problems**: at step `j`, add the interpolation terms and any extra constraint duals (Lipschitz, etc.) associated with step `j+1`.

- S contribution:
  - Use the currently selected verified decomposition. For the initial
    known/direct candidate, subtract its corresponding per-step S pieces;
    for example, `S_piece[i]` from `S = sum_i S_piece[i]`.
  - When Step 5 selects an alternative verified trial, use that trial's pieces
    and assignment instead of reverting to the first decomposition.
  - For numerical LDL pieces, match D/ell indices, preserve off-diagonal blocks
    and the chosen factor-to-step assignment. Do not reverse only the ell index.

This preference is important: a proof-specific S decomposition often carries
the interpretable vectors needed by `lyap-vectors` and `lyap-closed-form`.
Generic LDL may verify numerically but can obscure the intended closed-form
Lyapunov structure.

The following default assignment implements the directed example below for every applicable interpolation group. Adapt the assignment for additional star directions, reverse-consecutive pairs, operators, extras, and proof-specific S pieces. A missing assignment is an error, not a discarded contribution.

Use `-1` for the initial contribution, `0..N_int-1` for step contributions, and `"boundary"` for justified terminal leftovers. A deliberately omitted numerical term must be labeled `"omitted"` and pass the combined weighted-residual check in Step 6. Save the actual finalized assignments with the grouping source; do not assume one LDL factor per iteration.

```python
# (continuing from Steps 1-3; use the selected verified S_piece_terms)
grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1  # Candidate boundary rule; each may be 0, 1, or 2.
group_terms = {
    name: term for name, term in weighted_terms.items()
    if name != tau_name and np.any(np.asarray(saved_duals[name], dtype=float) != 0)
}

def idx(tag, N=N_int):
    suffix = tag.split("_")[1]
    return int(suffix) if suffix.isdigit() else N + 1

term_assignment = {}
for name in group_terms:
    pair = interpolation_pairs.get(name)
    if pair is None:
        continue  # Assign extras and constraints without point-pair labels explicitly.
    i, j = (idx(tag) for tag in pair)
    if i == N_int + 1 and j == 0:
        term_assignment[name] = -1
    elif (i == j - 1 or i == N_int + 1) and 1 <= j <= N_int:
        term_assignment[name] = j - 1
# Add the actual remaining assignments here, including every extra and boundary term.
# Define S_assignment = {piece_label: step_or_boundary, ...} from the verified pieces.
if set(term_assignment) != set(group_terms) or set(S_assignment) != set(S_piece_terms):
    raise ValueError("Assign every active constraint contribution and S piece")
allowed_assignments = set(range(-1, N_int)) | {"boundary", "omitted"}
if any(step not in allowed_assignments for step in term_assignment.values()):
    raise ValueError("Invalid constraint-to-step assignment")
if any(step not in allowed_assignments - {"omitted"} for step in S_assignment.values()):
    raise ValueError("Invalid S-piece assignment")

lyap = [pf.Scalar.zero()]
partial_sum = sum((group_terms[name] for name, step in term_assignment.items()
                   if step == -1), pf.Scalar.zero())
partial_sum -= sum((S_piece_terms[name] for name, step in S_assignment.items()
                    if step == -1), pf.Scalar.zero())
for step in range(N_int):
    partial_sum += sum((group_terms[name] for name, target in term_assignment.items()
                        if target == step), pf.Scalar.zero())
    partial_sum -= sum((S_piece_terms[name] for name, target in S_assignment.items()
                        if target == step), pf.Scalar.zero())
    lyap.append(partial_sum)

# Rank profile
ranks = []
for k, Vk in enumerate(lyap):
    M = pm.eval_scalar(Vk).inner_prod_coords.astype(float)
    rank = int(np.linalg.matrix_rank(M, tol=rank_tolerance))
    ranks.append(rank)
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()

retained_ranks = ranks[rank_left:N_int + 1 - rank_right]
print("Interior rank is constant at this N:",
      len(retained_ranks) >= 3 and len(set(retained_ranks)) == 1,
      "boundary exclusions:", (rank_left, rank_right))
```

---

## Step 5 - Diagnose Rank Structure Across Horizons

A good numerical observation has the same interior rank at two or more distinct horizons, using one construction recipe and a fixed boundary rule. Choose `rank_left, rank_right` in `0..2`: these count excluded indices from each end, including `V_0` and `V_N`. The retained indices are `rank_left .. N-rank_right`. Require at least three retained indices at each confirming horizon; an empty or singleton comparison is not evidence. For example, `(2, 2)` retains `V_2 .. V_{N-2}`. The excluded terms remain in `lyap` and in coverage, basis reconstruction, and the final proof.

Equal ranks do not imply equal column spaces or a discovered basis. A growing or inconsistent rank is a diagnostic: inspect indexing, endpoint effects, numerical singular values, and the decomposition/grouping choices. Record the tolerance and scaling convention and keep them comparable across horizons; do not adjust a cutoff to force agreement. An ambiguous numerical rank does not confirm a pattern. If the monotonicity direction is wrong, correct the sign convention and recheck all scalar components before using that candidate.

**Recovery before stopping:**

1. Inspect the current candidate, then try meaningfully different interpolation groupings, assignments of SOS pieces to steps/boundaries, and alternative verified decompositions of the same S. Reordering one fixed decomposition several times does not exhaust the search. Use reverse LDL first when a fresh generic factorization is appropriate; if it gives unhelpful partial sums, other basis orderings or structural square decompositions may be explored with reconstruction/sign checks. No outside solution is needed or authorized by this recovery.
2. If no useful observation emerges, increase the horizon within the same attempt, normally `4, 6, 8, 10, 12`, starting from the selected `N_verify` (often 6 for a complex algorithm). Useful intermediate horizons are allowed. Return to Block 2 for a complete certificate at each new N, then repeat Steps 1-6 here. Each horizon has its own lambda, S, extras, coordinates, and certificate ID. Preserve earlier samples under the notebook's sibling `supplementary/`; do not merely change N on old arrays. Reuse the existing initial closed-form search when applicable without requiring analytic global formulas.
3. Carry a consistent construction recipe across the samples. A recipe identifies the source/algorithm, parameter normalization, relaxed-constraint rule, S-decomposition strategy, and term-assignment rule, including their dependence on N. Changing a recipe or boundary rule requires rechecking the comparison; do not select unrelated favorable samples at different horizons. A numerical optimal certificate at one N is not literally the certificate at another N.
4. Confirm a promising pattern at another adequate horizon and continue to Block 4 once rank and coverage checks pass. Reuse available samples; do not visit every remaining horizon after confirmation. This block does not require finding or reconstructing the special basis, which belongs to Block 4. A pattern first found at 12 may be checked at an earlier adequate horizon; confirmation does not authorize 14.
5. Keep exploring feasible, meaningfully different candidates and larger horizons through **N=12** before treating a small-N rank failure as a reason to stop. Respect the original time/resource budget. If a usable sample at 12 cannot be obtained, report the actual obstruction and tested horizons instead of claiming rank failure through 12. Distinguish a failed solve, an invalid certificate, ambiguous rank, and a valid but inconsistent profile.
6. Before any **N>12** exploration, ask the user for a bounded extension, for example: "No rank pattern was confirmed through N=12. May I try N=14 and N=16 within the remaining budget?" Honor prior explicit authorization for that range; otherwise do not proceed without an answer approving it. Approval for larger N does not itself extend the time budget. In an automated evaluation, report the operational request as `awaiting_horizon_approval`; use `stopped_at_horizon_limit` if declined and `timeout` if the unchanged deadline expires. A few failed groupings or a small-N rank mismatch alone is not `needs_guidance`.

The following comparison operates on **recomputed observations**, not unchecked saved flags. After Steps 1-6 at each sample, record its `N`, `certificate_id`, `recipe_id`, `rank_profile`, `rank_convention` (tolerance, scaling, and coordinate-order rules, not horizon-specific label arrays), `rank_credible`, `certificate_checked`, and `grouping_checked`. Keep one selected trial per horizon for the recipe being compared; preserve other trials separately. Singular-value evidence and executed source accompany the records. Rank constancy is finite-sample discovery evidence, not an arbitrary-horizon theorem.

```python
def assess_rank_pattern(samples, selected_certificate_id, left=1, right=1):
    if type(left) is not int or type(right) is not int or not (0 <= left <= 2 and 0 <= right <= 2):
        raise ValueError("Exclude at most two indices at each end")
    selected = [s for s in samples if s["certificate_id"] == selected_certificate_id]
    if len(selected) != 1:
        raise ValueError("Select exactly one current certificate observation")
    selected = selected[0]
    family = [s for s in samples if s["recipe_id"] == selected["recipe_id"]]
    if any(s["rank_convention"] != selected["rank_convention"] for s in family):
        raise ValueError("Recompute the candidate with comparable rank conventions")
    if len({s["N"] for s in family}) != len(family):
        raise ValueError("Compare one selected trial per horizon for this recipe")
    eligible, unresolved, inconsistent = [], [], False
    for sample in family:
        n, profile = sample["N"], sample["rank_profile"]
        if type(n) is not int or n < 1 or len(profile) != n + 1:
            raise ValueError("Rank profile must contain V_0 through V_N")
        if any(type(r) is not int or r < 0 for r in profile):
            raise ValueError("Ranks must be nonnegative integers")
        retained = profile[left:n + 1 - right]
        if not (sample["certificate_checked"] is True and sample["grouping_checked"] is True):
            unresolved.append({"N": n, "reason": "unverified_certificate_or_grouping"})
        elif sample["rank_credible"] is not True:
            unresolved.append({"N": n, "reason": "ambiguous_rank"})
        elif len(retained) < 3:
            unresolved.append({"N": n, "reason": "insufficient_interior_indices"})
        elif len(set(retained)) != 1:
            inconsistent = True
            unresolved.append({"N": n, "reason": "nonconstant_interior_rank"})
        else:
            eligible.append((n, retained[0], sample["certificate_id"]))
    common_ranks = {r for _, r, _ in eligible}
    inconsistent = inconsistent or len(common_ranks) > 1
    selected_eligible = any(cid == selected_certificate_id for _, _, cid in eligible)
    confirmed = not inconsistent and len(eligible) >= 2 and selected_eligible
    return {
        "status": "confirmed" if confirmed else "inconsistent" if inconsistent else "insufficient_evidence",
        "boundary_exclusions": {"left": left, "right": right},
        "rank": next(iter(common_ranks)) if len(common_ranks) == 1 else None,
        "confirmed_horizons": sorted(n for n, _, _ in eligible) if confirmed else [],
        "selected_certificate_id": selected_certificate_id,
        "recipe_id": selected["recipe_id"],
        "rank_convention": selected["rank_convention"],
        "unresolved_samples": unresolved,
    }
```

Apply the chosen boundary rule to all samples of the candidate; do not omit a valid contradictory profile to manufacture confirmation. A diagnostic failure returns to the recovery above. Record unsuccessful or budget-limited work honestly without marking Block 3 complete.

---

## Step 6 — Verify Coverage

The final partial sum `lyap[N]` should be expressible using nearly all dual terms from the Full-PEP proof. Check that at most one interpolation inequality and at most one S square term are left out (these become the boundary terms in the final proof):

Record coverage by actual constraint name and S-piece label. The built-in normalization term belongs to the boundary argument; zero-valued multipliers remain in the certificate inventory. The final residual must retain all Gram, function-value, and offset coordinates. Rank alone cannot set `grouping_checked`. Run these coverage checks for every horizon/candidate used to confirm the rank pattern. The boundary index exclusions in Step 5 do not change the permitted leftover terms here.

The PSD-piece check below illustrates a decomposition into squares or PSD blocks. If an applicable known direct construction establishes the sign through a different combined identity, retain that construction and its verified sign argument, and adapt the checks to its full scalar terms. Do not discard verified direct/per-step cases merely to fit this example.

```python
boundary_names = [name for name, step in term_assignment.items() if step == "boundary"]
boundary_S = [name for name, step in S_assignment.items() if step == "boundary"]
if sum(name in interpolation_terms for name in boundary_names) > 1 or len(boundary_S) > 1:
    raise ValueError("Revisit the permitted terminal interpolation/S leftovers")
omitted = sum((group_terms[name] for name, step in term_assignment.items()
               if step == "omitted"), pf.Scalar.zero())
leftover = sum((group_terms[name] for name in boundary_names), pf.Scalar.zero())
leftover -= sum((S_piece_terms[name] for name in boundary_S), pf.Scalar.zero())
coverage_diff = (lyap[N_int] + leftover + omitted
                 - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar))
piece_diff = sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar
for label, expression in (("coverage", coverage_diff), ("S pieces", piece_diff), ("omitted", omitted)):
    value = pm.eval_scalar(expression)
    for coords in (value.inner_prod_coords, value.func_coords, np.asarray(value.offset)):
        if not np.allclose(np.asarray(coords, dtype=float), 0,
                           atol=tol["identity_atol"], rtol=tol["identity_rtol"]):
            raise ValueError(f"Full-coordinate {label} check failed")
# Every subtracted S piece must have the nonnegative numerical sign used here.
for name, piece in S_piece_terms.items():
    value = pm.eval_scalar(piece)
    matrix = np.asarray(value.inner_prod_coords, dtype=float)
    if not np.allclose(value.func_coords, 0, atol=tol["identity_atol"], rtol=0) or not np.allclose(value.offset, 0, atol=tol["identity_atol"], rtol=0):
        raise ValueError(f"S piece has unexpected function/offset terms: {name}")
    if matrix.size and np.linalg.eigvalsh((matrix + matrix.T) / 2).min() < -tol["psd_tol"]:
        raise ValueError(f"S piece has the wrong numerical sign: {name}")
# Step identities follow the chosen assignments; check them, including the initial terms.
for k in range(N_int):
    assigned_steps = {-1, 0} if k == 0 else {k}
    increment = sum((group_terms[name] for name, step in term_assignment.items()
                     if step in assigned_steps), pf.Scalar.zero())
    increment -= sum((S_piece_terms[name] for name, step in S_assignment.items()
                      if step in assigned_steps), pf.Scalar.zero())
    value = pm.eval_scalar(lyap[k + 1] - lyap[k] - increment)
    for coords in (value.inner_prod_coords, value.func_coords, np.asarray(value.offset)):
        if not np.allclose(np.asarray(coords, dtype=float), 0,
                           atol=tol["identity_atol"], rtol=tol["identity_rtol"]):
            raise ValueError(f"Partial-sum increment identity failed at k={k}")
grouping_checked = True
M_final = pm.eval_scalar(lyap[N_int]).inner_prod_coords.astype(float)
rank_final = int(np.linalg.matrix_rank(M_final, tol=rank_tolerance))
print(f"lyap[{N_int}] rank:", rank_final)
print("Coverage checked with all scalar components and explicit boundary leftovers.")
```

Explain how the normalized inequality contributions and the subtracted PSD pieces give the numerical nonincreasing convention, and record which boundary contributions still require analytic sign/domain justification. Numerical sign tolerances and rank evidence do not establish the universal Lyapunov theorem. An omitted numerical term remains an explicit unresolved exact-proof obligation for Block 5.

---

## Step 7 — Save State

Serialize every partial sum's Gram, function-value, and constant coordinates. Capture `certificate_check_code`, `decomposition_code`, and `grouping_code` from the actual executed source: no verification placeholders or manually retyped second grouping loop. The check source reconstructs and verifies the saved certificate; the decomposition source constructs the selected pieces; the grouping source includes finalized assignments, construction, rank, and coverage/sign checks and recomputes `grouping_checked`. They consume the rebuilt setup and the `certificate` state alias, without solving.

Keep known direct/per-step S definitions and any lambda/S candidates with their current status. These source fields can contain applicable legacy mathematical definitions, but must not require an old live `result`. Recover and verify old source dependencies coherently before handoff. The main notebook shows the actual mathematical code; `exec` calls or saved flags do not replace it.

Keep multi-horizon trials and their executed source under the notebook's sibling `supplementary/`. Select one complete horizon-specific certificate for the Block 3/4 handoff. If this changes the selected Block 2 certificate, update its state and dependent source coherently; archive the prior sample. A legacy state may be recovered without this metadata, but do not describe it as newly confirmed across horizons.

```python
import json, os
os.makedirs("examples_peppy/{ALGO_NAME}/state", exist_ok=True)
if not certificate_checked or not grouping_checked:
    raise ValueError("Finish certificate and grouping checks before saving Block 3")
if not all(isinstance(source, str) and source.strip()
           for source in (certificate_check_code, decomposition_code, grouping_code)):
    raise ValueError("Capture the exact executed check/decomposition/grouping source")
# rank_samples contains observations recomputed with this candidate recipe.
rank_search = assess_rank_pattern(rank_samples, certificate["certificate_id"],
                                  left=rank_left, right=rank_right)
selected_observation = next(s for s in rank_samples
                            if s["certificate_id"] == certificate["certificate_id"])
if selected_observation["N"] != N_int or selected_observation["rank_profile"] != ranks:
    raise ValueError("Selected rank evidence differs from this certificate/partial sums")
if rank_search["status"] != "confirmed":
    raise ValueError("Continue Step 5 recovery or report the actual incomplete status")
notebook_dir = Path("examples_peppy/{ALGO_NAME}")  # Use the actual selected notebook directory.
rank_evidence_path = notebook_dir / "supplementary" / "rank_search.json"
rank_evidence_path.parent.mkdir(parents=True, exist_ok=True)
rank_search["evidence_path"] = rank_evidence_path.relative_to(notebook_dir).as_posix()
rank_evidence_path.write_text(json.dumps({"summary": rank_search, "samples": rank_samples},
                                       indent=2, allow_nan=False), encoding="utf-8")
evaluated_lyap = [pm.eval_scalar(Vk) for Vk in lyap]
state = {
    **certificate,
    "rank_profile": ranks,
    "rank_search": rank_search,
    "lyap_inner_prod_coords": [np.asarray(v.inner_prod_coords, dtype=float).tolist()
                              for v in evaluated_lyap],
    "lyap_func_coords": [np.asarray(v.func_coords, dtype=float).tolist() for v in evaluated_lyap],
    "lyap_offsets": [float(v.offset) for v in evaluated_lyap],
    "certificate_check_code": certificate_check_code,
    "decomposition_code": decomposition_code,
    "grouping_code": grouping_code,
    "extra_duals": extra_duals,
    "rank_tolerance": rank_tolerance,
    "reconstruction_tolerance": tol["reconstruction_atol"],
    "reconstruction_rtol": tol["reconstruction_rtol"],
    "grouping_coverage": {
        "constraint_assignment": term_assignment,
        "S_assignment": {str(key): value for key, value in S_assignment.items()},
        "normalization_constraint": tau_name,
        "boundary_constraints": boundary_names,
        "boundary_S": [str(key) for key in boundary_S],
        "omitted_constraints": [name for name, step in term_assignment.items() if step == "omitted"],
        "checked": grouping_checked,
    },
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": certificate.get("analytic_full_pep_verified", False),
    "lyapunov_proof_verified": False,
}
with open("examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json", "w", encoding="utf-8") as fh:
    json.dump(state, fh, indent=2, allow_nan=False)
print("State saved to examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json")
print("Rank profile:", ranks)
```

Keep the three statuses separate. Null `lamb_code` or `S_code` remains null; do not manufacture a zero formula. An existing usable analytic-path state remains supported through complete coherent recovery. Saving Block 3 numerical exploration does not certify an analytic full-PEP or Lyapunov proof.

---

## Step 8 — Update Lyapunov Notebook

Open the existing notebook and add or replace the Lyapunov partial-sum section, following the `Identify the vectors composing the Lyapunov function` lead-in from `examples_peppy/_references/gd/gd_example_lyap.ipynb`.

The notebook cells for this block must show:
- the reconstructed saved-certificate identity and its numerical status, with all Gram/function/offset checks visible
- extraction of interpolation duals and extra constraint duals
- LDL/direct S ingredients used in the partial sums
- the actual `lyap = [...]`, `partial_sum = ...`, and update loop; do not hide this behind `exec(grouping_code)`
- rank profile computation inside the visible partial-sum construction cell
- a concise cross-horizon summary with the fixed boundary rule, common rank, confirming horizons, and tolerance/scaling convention
- coverage check for `lyap[N]`

Make the first Block 3 notebook cell human-interpretable. It should summarize the partial-sum increments in rendered LaTeX, for example `$$V_{k+1} - V_k = c_1\operatorname{Lip}(x_{k+1/2}, x_{k+1}) + c_2\operatorname{Mon}(x_k, x_{k+1})$$`, and explain the rank profile and coverage residual in words. Do not print these equations as monospace text output when they can be displayed as Markdown/LaTeX. Do not expose raw JSON dictionaries such as `grouping_terms` as the primary notebook output; raw state dumps may be kept only as optional debug details.

In the visible partial-sum construction cell, print the rank of each constructed Lyapunov term immediately after building `lyap`, one line per term. Print a blank line after `rank V_0: ...`, then print the interior-rank consistency check in the same cell. Use the selected `rank_left, rank_right` from the construction. This is a within-horizon diagnostic; the cross-horizon comparison in Step 5 is separate:

```python
ranks = []
for k, Vk in enumerate(lyap):
    matrix = pm.eval_scalar(Vk).inner_prod_coords.astype(float)
    rank = int(np.linalg.matrix_rank(matrix, tol=rank_tolerance))
    ranks.append(rank)
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()

retained_ranks = ranks[rank_left:N_int + 1 - rank_right]
print("Interior rank is constant at this N:",
      len(retained_ranks) >= 3 and len(set(retained_ranks)) == 1,
      "boundary exclusions:", (rank_left, rank_right))
```

Do not create a separate `### Rank Profile` cell just to print the stored and computed rank lists or coefficient matrices. Do not print the grouped dual terms by default, e.g. avoid output like `V_k terms:` followed by every `(kind, ri, ci, coeff)` entry. The construction code should remain visible, but its primary output should be the rank profile in the line-by-line format above and the single interior-rank consistency line.

If producing that readable summary requires new nontrivial formatting helpers, place them in `examples_peppy/{ALGO_NAME}/supplementary/notebook_helpers.py` or another small module under the notebook's sibling `supplementary/`, and call them using an explicit path relative to the selected example directory. The notebook should show the summary output and a simple helper call, not long helper definitions such as fraction formatters, tag renderers, or residual-name pretty-printers. Do not hide the actual partial-sum construction, rank computation, or coverage check in this helper; those remain visible notebook workflow code.

Keep these cells executable with the state files under `examples_peppy/{ALGO_NAME}/state/`.

For notebook Markdown cells added or edited in this block, use `$...$` for inline math and `$$...$$` for display math. Verify their rendered appearance, not just their source delimiters, and record any unresolved rendering issue in the supplementary checklist.

If a separate file is created or reused to justify a proof condition in this block, include its relevant identity definitions, actual checks/results, and reasoning in the notebook under the [proof verification rule](../../../references/output-layout.md#proof-verification-files-during-notebook-authoring). Reuse existing cells. Preserve the numerical handoff and explicit unresolved analytic status; this adds no earlier analytic-proof prerequisite.

Update the notebook's sibling `supplementary/<notebook-stem>_checklist.md` with this block's actual cell references, evidence, and unresolved requirements, following Block 1's Notebook Lifecycle. Inspect every notebook requirement listed above; future-block work stays pending. Keep the record out of the notebook and routine completion report, and disclose any unresolved requirement due in this block.

---

## Output

Report:
- The selected rank profile `[r_0, r_1, ..., r_N]`, fixed left/right boundary exclusions, common interior rank, and confirming horizons; distinguish confirmed evidence from incomplete exploration
- Which dual terms are grouped at each step
- Whether `lyap[N]` has near-zero rank, and the full-coordinate boundary coverage result
- The separate numerical-certificate, analytic-full-PEP, and analytic-Lyapunov statuses; list unresolved formulas carried to later blocks

- Confirmation that the notebook was updated through the partial-sum/rank-profile section

**Next step**: `/lyap-vectors {ALGO_NAME}` after rank and coverage checks pass. Otherwise continue the authorized recovery or report the actual pending approval, obstruction, or budget limit without marking Block 3 complete.
