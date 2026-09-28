# /pep-full-proof: PEPFlow Block 2 — Finding Full-PEP-Style Proof

Find a tight performance guarantee, capture and verify a complete numerical dual certificate, and attempt closed-form formulas before numerical Lyapunov discovery.

> $ARGUMENTS  (ALGO_NAME, e.g. `heavy_ball`)

---

## Environment

PEPFlow repo root: `$(git rev-parse --show-toplevel)/`
Python executable: `.venv/bin/python3`
Input: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json`
Output: `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json`
Notebook: update `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb`

## Output Layout

Before creating files, read and follow [the shared output layout](../../plugins/peppy-workflow/references/output-layout.md). Resolve the example paths below from the actual output notebook directory, including when it is under `examples_peppy/`.

---

## Reference Scope

When looking for reference examples, notebook structure, proof-writing patterns, or prompt skeletons, use only files under `examples_peppy/`. The `examples_peppy/_references/` subtree is explicitly allowed and may be used freely as reference material. Do not inspect or follow other repository example/reference files outside `examples_peppy/` for this workflow.

---

## Progression and Proof Status

The default path first reviews applicable known formulas and makes a meaningful, focused closed-form search for unresolved lambda and S formulas. Reuse established formulas whose assumptions match; do not rediscover them. Success is not required for proceeding to numerical partial sums. Record what was inspected or tried and which formulas remain unresolved; do not repeat searches or request user insight solely because no closed form was found.

A reliable numerical certificate is still mandatory. Missing duals, inconsistent components, failed numerical identities, unsupported normalization, or unresolved numerical failures block the handoff. If the user explicitly requests an analytic full-PEP proof itself, preserve that goal: numerical progress is useful partial work, not completion of that request.

Keep three independent booleans: `numerical_certificate_verified`, `analytic_full_pep_verified`, and `lyapunov_proof_verified`. Finite-sample agreement, a fitted formula, or a legacy `proof_valid` flag does not establish either analytic claim. A final Lyapunov proof may succeed without a separate analytic full-PEP proof.

For a return from Block 3 at an additional horizon, follow its authorized recovery policy and acquire or revalidate one complete certificate at that N. Carry the candidate relaxation/decomposition recipe across horizons, adapting its index pattern to the new context. Reuse valid saved samples and applicable dense/sparsity evidence; perform only the new acquisition and checks needed for this sample. Keep each sample's lambda, S, scalar/PSD extras, normalization, coordinates, setup, solver settings, and checks together. No analytic global lambda/S formula is required for cross-horizon rank comparison.

Before replacing the selected sample, preserve its complete state, solver results, and dependent diagnostics in the notebook-adjacent `supplementary/`, identified by horizon and certificate ID. Keep exploratory samples there until selected. Update the selected B2/B3 handoff coherently and rebuild its dependent partial sums and basis data; changing only `N_verify` is not a valid handoff.

## Step 1 — Load State

Run this block's dependent Python fragments in one process or notebook kernel, starting at the repository root. Resolve the paths from the actual notebook directory. The existing runner returns a partial numerical summary, so the selected certificate below is captured directly from one live solve; do not add a package-level restoration API.

```python
import json, fractions, hashlib, importlib.util, uuid
from importlib.metadata import version
from pathlib import Path
import numpy as np
import sympy as sp
import pepflow as pf
from pepflow.pep_runner import run
from pepflow.constraint import ScalarConstraint, PSDConstraint
from pepflow.operator import LinearOperatorTranspose
from pepflow.utils import Comparator

repo_root = Path.cwd().resolve()
notebook_dir = repo_root / 'examples_peppy/{ALGO_NAME}'
state_dir = notebook_dir / 'state'
b1 = json.loads((state_dir / '{ALGO_NAME}_b1.json').read_text(encoding='utf-8'))
N_int = b1['N_verify']  # Initial sample; use the authorized Block 3-requested N on return.
N = sp.S(N_int)
params = json.loads(b1['params_json'])
params_sp = {
    key: (sp.Rational(value) if isinstance(value, str)
          else sp.nsimplify(value, rational=True, tolerance=1e-9)
          if isinstance(value, float) else sp.S(value))
    for key, value in params.items()
}
setup_file = notebook_dir / '{ALGO_NAME}_setup.py'
OBJ_TAG = b1['obj_tag']
tau_name = b1.get('tau_name', 'initial_condition')
spec = importlib.util.spec_from_file_location('_pepflow_setup', setup_file)
if spec is None or spec.loader is None:
    raise ImportError(f'Cannot load {setup_file}')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert Path(pf.__file__).resolve() == repo_root / 'pepflow/__init__.py'
# Include any other local modules imported by the setup or used in its certificate.
source_paths = [setup_file, *sorted((repo_root / 'pepflow').glob('*.py'))]
source_hashes = {str(path.relative_to(repo_root)).replace('\\', '/'):
                 hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths}
lamb_code = S_code = None
formula_status = {'lambda': 'unresolved', 'S': 'unresolved'}
closed_form_search = {'completed': False, 'references_reviewed': [],
                      'attempts': [], 'unresolved_components': ['lambda', 'S']}
numerical_certificate_verified = analytic_full_pep_verified = False
lyapunov_proof_verified = False
require_analytic_full_pep = bool(b1.get('require_analytic_full_pep', False))
for key in ('algo_name', 'problem_type', 'obj_tag', 'params_json',
            'N_verify', 'conjectured_rate'):
    print(f'{key}: {b1[key]}')
```

On a Block 3 return, set `N_int` to the requested horizon before constructing `N` or any context. Preserve the applicable earlier `closed_form_search` record and reusable formula source/status after the initialization above, with the source certificate and applicability recorded; compare any reused candidate formulas against the new sample. A new N alone does not require repeating a completed initial lambda/S search. Search again only where the earlier attempt or formula is no longer applicable, and preserve unresolved components honestly.

Confirm the actual initial-constraint name, normalization, and target rate from the setup; use its name as `tau_name` even when it differs from the default. Restart the process after changes to imported source. Set `require_analytic_full_pep=True` when the user explicitly requests an analytic full-PEP proof; otherwise inherit the flag, defaulting to false. Numerical continuation does not complete that separate requested goal.

---

## Step 2 — Dense Solve

Run a dense solve at `N = N_VERIFY`:

```python
dense_data = run(str(setup_file), N_int, params, tau_name=tau_name)
(state_dir / '{ALGO_NAME}_dense.json').write_text(
    json.dumps(dense_data, indent=2, allow_nan=False), encoding='utf-8')
```

The runner summarizes the returned function/operator. If other objects or constraint families are relevant to choosing the relaxation, inspect them from a direct dense solve using the same setup/capture pattern as Step 3. Do not mistake a single displayed group for the complete certificate.

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

```python
import json, numpy as np

data = dense_data
if "lambda_groups" in data:
    raise ValueError("Adapt the sparsity example to the actual constraint groups")

N = data["N"]
row_names = data["lambda_row_names"]
col_names = data["lambda_col_names"]
lamb = np.array(data["lambda_matrix"])
OBJ_TAG = b1["obj_tag"]

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
```

Test each proposed relaxation on a fresh builder; its relaxation setter appends names. All selected lambda groups, extra duals, S, and bound values must come from this one result:

```python
ctx, pb, obj = mod.get_pep_setup(sp.S(N_int), params_sp)
if relaxed:
    pb.set_relaxed_constraints(relaxed)
result = pb.solve(resolve_parameters=params_sp)  # Existing primal solve API.
assert result.context is ctx and pb.ctx is ctx
ctx.set_as_current()
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
S_sol = result.get_gram_dual_matrix()
tau_sol = result.get_dual_value(tau_name)
if tau_sol is None or not np.isfinite(float(result.opt_value)):
    raise ValueError('The selected solve has no usable bound')
numerical_certificate_verified = False
preserved = abs(float(dense_data['opt_value']) - float(result.opt_value)) < 1e-5
print(f"Dense: {dense_data['opt_value']:.8f}  Relaxed: {result.opt_value:.8f}  Preserved: {preserved}")

entries = [(c, 'initial', None, None) for c in pb.init_conditions]
for owner in [*ctx.func_to_triplets, *ctx.oper_to_duplets]:
    if isinstance(owner, LinearOperatorTranspose):
        continue
    groups = ctx.get_constraint_data(owner)
    entries.extend((c, 'interpolation', str(owner), str(group))
                   for group, constraints in groups.sc_dict.items() for c in constraints)
    entries.extend((c, 'interpolation', str(owner), str(group))
                   for group, c in groups.psd_dict.items())
assert len({c.name for c, *_ in entries}) == len(entries)
constraint_metadata, named_dual_values = {}, {}
for c, origin, owner, group in entries:
    is_scalar = isinstance(c, ScalarConstraint)
    if not is_scalar and not isinstance(c, PSDConstraint):
        raise TypeError(f'Unsupported constraint: {c.name}')
    dropped = c.name in pb.relaxed_constraints
    value = result.get_dual_value(c.name)
    if value is None and not dropped:
        raise ValueError(f'Missing active dual: {c.name}')
    if value is not None and not np.all(np.isfinite(np.asarray(value, dtype=float))):
        raise ValueError(f'Nonfinite dual: {c.name}')
    shape = [] if is_scalar else list(np.asarray(c.lhs - c.rhs).shape)
    if value is not None and list(np.asarray(value).shape) != shape:
        raise ValueError(f'Dual shape mismatch: {c.name}')
    constraint_metadata[c.name] = dict(origin=origin, owner=owner, group=group,
        kind='scalar' if is_scalar else 'psd', comparator=c.cmp.value,
        shape=shape, relaxed=dropped)
    named_dual_values[c.name] = (None if dropped else float(value) if is_scalar
                               else np.asarray(value, dtype=float).tolist())
assert set(pb.relaxed_constraints).issubset(constraint_metadata)
assert tau_name in {c.name for c in pb.init_conditions}
assert constraint_metadata[tau_name]['kind'] == 'scalar'
assert not constraint_metadata[tau_name]['relaxed']
```

Use every owner's scalar and matrix groups; preserve constraint names, comparators, and matrix shapes. `get_dual_value` can return matrix values despite its narrow annotation. Equality multipliers are unrestricted; inequality scalar multipliers and semidefinite multipliers have their actual cone signs. Reporting small values does not authorize discarding their proof contributions.

- **Preserved**: retain `(ctx, pb, obj, result)` and its entire captured certificate for the remaining steps.
- **Not preserved**: expand to Hypothesis 2, including skip-one pairs (`|i-j| == 2`), and retest. Do not hand off a failed relaxation as a valid certificate.

**Find pattern at your discretion**: Consecutive index pairs are often, but not always, the right choice. For example, there are cases where (N, j) index pairs should be used. Inspect the dense λ and use your judgement to include the important-looking ones.

**Nontrivial checkpoint**: If no small sparsity pattern can be found that preserves the rate (even expanded hypothesis fails), display the dense λ fully and ask the user which entries look structurally important.

---

## Step 4 — Inspect Relaxed λ and Guess Closed Form

Review the permitted references and prior formulas for the current algorithm, normalization, and parameter domain. Record them in `closed_form_search['references_reviewed']`. For each unresolved group, inspect fractions, index/horizon/parameter dependence, and plausible formulas using the selected certificate. This initial attempt is mandatory unless an applicable established formula can be reused; it need not be exhaustive.

```python
assert preserved
for name, value in named_dual_values.items():
    meta = constraint_metadata[name]
    if value is not None and meta['kind'] == 'scalar' and abs(value) > 1e-6:
        print(name, value, fractions.Fraction(value).limit_denominator(1000))
```

A proposed `lamb(ri, ci)` or grouped candidate should be compared to the matching current numerical values at the existing `atol=1e-4`. Carry every active function/operator group and extra term; a successful comparison for one group does not verify the others. Keep the executed candidate source in `lamb_code` and its check outcome in the initial-search record. Use `None` when no usable definition exists; never substitute a zero-returning placeholder.

**Algorithm parameters**: The analytical values may not always be a nice rational number. In such cases, consider building connection with the parameters used in the algorithm definition (update rule).

Use `formula_status['lambda'] = 'candidate'` for a numerically supported formula and `'verified'` only when its analytic validity over the stated domain has been established. Record the domain and proof evidence in the notebook/state. If no clean formula emerges, retain `'unresolved'`, record what was tried, and continue with the consistent numerical values. Do not request a user checkpoint solely for this missing formula.

---

## Step 5 — Decompose S

Before computing a new LDL factorization, inspect whether the algorithm already
has a proof-specific S decomposition in the state, reference notebooks/modules,
or prior proof cells. In particular, if `examples_peppy/_references/{ALGO_NAME}/`
exists, search it for names and patterns such as `S_guess`, `S_piece`,
`S_decomp`, `square`, `remainder`, `rank V`, `lyap`, or `partial_sum`.

If a reference contains a verified decomposition, such as `S_guess` matching the
certificate matrix or a sum like `S_guess1 + S_guess2 + ...`, adapt that
decomposition first and store it in the Block 2 state as executable `S_code`.
When possible, also store named square families or per-step pieces so Block 3
can subtract those same proof-specific pieces when constructing `V_k`.

Do not treat the absence of serialized S pieces in an existing state file as
evidence that no known decomposition exists. A reference notebook may contain
the intended decomposition only as executable notebook code. Use LDL only after
you have checked the reference sources and either found no known decomposition
or explicitly verified that the known decomposition is insufficient for the
certificate being built.

### 5a — LDL decomposition

Use the selected numerical S and its original coordinate order; do not solve again merely to obtain S.

```python
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

basis = ctx.basis_vectors()
D, ell = ldl_decompose_with_reversed_basis(S_sol, basis, print_output=True)
D = np.asarray(D, dtype=float)
E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
numerical_decomposition = {'method': 'reverse_ldl', 'D': D.tolist(),
    'ell_coords': E.tolist(), 'basis_labels': [str(v) for v in basis]}
S_numeric = sum((float(D[i, j]) * ell[i] * ell[j]
                 for i, j in np.ndindex(D.shape)), pf.Scalar.zero())
print('D diagonal:', [round(float(D[i, i]), 6) for i in range(len(D))])
print('ell vectors:', [str(v) for v in ell])
```

Rows of `ell_coords` are factor coordinates in the original basis, so `S = E.T @ D @ E`. Retain off-diagonal LDL blocks and matched factor indices; do not assume an LDL index is an iteration index. Near-zero values may be hidden in a display, but omitting them from the decomposition requires a successful reconstruction check. Reversed-basis LDL still requires the matching earlier-iterates-first basis/label convention; preserve verified proof-specific decompositions when available.

### 5b — Direct guess for low-rank S

When S has a promising low-rank structure, inspect square-term expressions and their index/parameter dependence as the initial S closed-form attempt. Retain useful `S_guess` definitions and their numerical comparison against this same S in `S_code`; do not overwrite the numerical certificate with an unchecked guess. The comparison must check Gram coordinates and zero function/offset components at the existing `atol=1e-4`.

For a numerical direct decomposition, set the same live variables `D`, `E`, `ell`, and `S_numeric` from the selected direct factors, and use `numerical_decomposition` with `method='direct'`, matching `D`, `ell_coords`, and `basis_labels`; skip the LDL call when these verified factors are available. For proof-specific pieces that are not stored in this factor form, additionally retain their executed reconstruction source and piece coordinates, and verify the sum against the selected S. Numeric factors are data for this N and parameter sample, not formulas for other horizons.

A clean analytic decomposition is optional for the default handoff. Set `formula_status['S']` to `'unresolved'`, `'candidate'`, or `'verified'` under the same distinction as lambda. If neither a usable numerical LDL nor a verified numerical direct decomposition is available, diagnose that numerical failure before grouping; do not label it merely an unresolved closed form.

After reviewing known formulas and making the initial attempts for unresolved lambda and S, fill `closed_form_search['attempts']` with brief actual methods/outcomes and candidate checks, update `unresolved_components`, and set `completed=True`. Reuse of established formulas counts when their applicability was checked. Keep this short record in the existing notebook and state; no separate search report is required.

Once the candidate lambda or S coefficients and their definitions exist, the agent may invoke the optional [localize-n-summation-proof](../../plugins/peppy-workflow/optional/localize-n-summation-proof/SKILL.md) skill for a required positivity, nonnegativity, or nonvanishing bottleneck, a proof-critical sum/index identity lacking a generic symbolic audit, or an identified substantial simplification of a complex valid global sign proof. Briefly state the target and follow the canonical procedure within the current task/resource budget without waiting for a separate skill request. Skip concise valid arguments, signs unused by the selected proof, and autonomous localization disabled by the user.

Keep the result and any remaining obligation in the existing notebook. If localization fails, preserve any existing valid global argument; sampled signs alone remain unproved. Localization adds no analytic gate to numerical Blocks 3 and 4: defer unresolved localization when appropriate and continue after the existing numerical handoff checks pass. Necessary signs must still be justified before the affected theorem is reported as proved.

---

## Step 6 — Verify the Numerical Certificate and Any Analytic Proof

Use the primal result captured above. Normalize each scalar inequality to `R <= 0` and each matrix inequality to `R << 0`: use `lhs-rhs` for `LE`/`PEQ`, and `rhs-lhs` for `GE`/`SEQ`. For equality use `lhs-rhs = 0` and the unrestricted primal equality multiplier. The complete certificate identity is

`performance_metric - opt_value - sum(d * R) - sum(trace(D * R)) + S_numeric = 0`.

This includes the initial constraints and their constants; `opt_value` is the numerical bound, not necessarily equal to a single normalization multiplier. Do not assume a function-gap metric or R-versus-R-squared normalization. A dual-form solver's equality convention differs; do not feed its values into this primal example without adapting and checking the sign convention.

```python
tolerances = dict(identity_atol=1e-5, identity_rtol=0.0,
    reconstruction_atol=1e-4, reconstruction_rtol=1e-5,
    dual_tol=1e-6, psd_tol=1e-6, dense_opt_atol=1e-5)
weighted_constraints = pf.Scalar.zero()
scalar_inequality_values, matrix_inequality_eigenvalues = [], []
for c, *_ in entries:
    meta, value = constraint_metadata[c.name], named_dual_values[c.name]
    if meta['relaxed']:
        assert value is None
        continue
    residual = c.lhs - c.rhs
    if c.cmp in (Comparator.GE, Comparator.SEQ):
        residual = -residual
    if meta['kind'] == 'scalar':
        weighted_constraints += float(value) * (pf.Scalar.zero() + residual)
        if c.cmp != Comparator.EQ:
            scalar_inequality_values.append(float(value))
    else:
        dual = np.asarray(value, dtype=float)
        if c.cmp != Comparator.EQ and not np.allclose(
                dual, dual.T, atol=tolerances['psd_tol'], rtol=0):
            raise ValueError(f'Asymmetric matrix dual: {c.name}')
        weighted_constraints += sum((float(dual[i, j]) * residual[j, i]
            for i, j in np.ndindex(dual.shape)), pf.Scalar.zero())
        if c.cmp != Comparator.EQ:
            matrix_inequality_eigenvalues.extend(np.linalg.eigvalsh((dual + dual.T) / 2))

diff = pb.performance_metric - float(result.opt_value) - weighted_constraints + S_numeric
checked = pm.eval_scalar(diff)
max_abs = lambda values: float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0.0))
S_array = np.asarray(S_sol.matrix, dtype=float)
S_reconstructed = E.T @ D @ E
S_eigenvalues = np.linalg.eigvalsh((S_array + S_array.T) / 2)
residuals = dict(
    identity_gram_max_abs=max_abs(checked.inner_prod_coords),
    identity_func_max_abs=max_abs(checked.func_coords),
    identity_offset_abs=max_abs(checked.offset),
    S_reconstruction_max_abs=max_abs(S_reconstructed - S_array),
    dense_relaxed_gap=abs(float(dense_data['opt_value']) - float(result.opt_value)),
    minimum_scalar_inequality_dual=min(scalar_inequality_values, default=0.0),
    minimum_S_eigenvalue=float(S_eigenvalues.min()) if S_eigenvalues.size else 0.0,
    minimum_matrix_inequality_eigenvalue=min(matrix_inequality_eigenvalues, default=0.0))
passed = (
    str(result.solver_status) == 'optimal'
    and np.all(np.isfinite(S_array))
    and np.allclose(S_array, S_array.T, atol=tolerances['psd_tol'], rtol=0)
    and all(residuals[key] <= tolerances['identity_atol'] for key in
            ('identity_gram_max_abs', 'identity_func_max_abs', 'identity_offset_abs'))
    and np.allclose(S_reconstructed, S_array, atol=tolerances['reconstruction_atol'],
                    rtol=tolerances['reconstruction_rtol'])
    and residuals['dense_relaxed_gap'] < tolerances['dense_opt_atol']
    and residuals['minimum_scalar_inequality_dual'] >= -tolerances['dual_tol']
    and residuals['minimum_S_eigenvalue'] >= -tolerances['psd_tol']
    and residuals['minimum_matrix_inequality_eigenvalue'] >= -tolerances['psd_tol'])
numerical_checks = {'tolerances': tolerances, 'residuals': residuals, 'passed': bool(passed)}
numerical_certificate_verified = bool(passed)
print('Numerical certificate verified:', numerical_certificate_verified)
print('Numerical residuals:', residuals)
assert numerical_certificate_verified, 'Diagnose the numerical certificate before proceeding'
```

Zero is recorded as the vacuous lower bound when an inequality family is empty. Record and diagnose any non-optimal status (including `optimal_inaccurate`) rather than silently promoting it. Any justified tolerance/solver-policy change must be explicit and followed by fresh checks; do not loosen tolerances just to pass. Compare the resulting bound with the requested conjecture and its normalization as well as the dense solve; unexplained mismatch still blocks progress.

This fixed-sample check verifies numerical consistency, not an all-parameter proof. When analytic formulas are available, separately assemble the exact full-PEP identity, verify every applicable Gram/function/constant component and sign/domain condition, and retain its actual proof evidence. Only then may `analytic_full_pep_verified=True`. Neither numerical agreement nor the existence of `lamb_code`/`S_code` sets that flag. The final Lyapunov proof flag remains false until Block 5 establishes its own complete analytic argument.

---

## Step 7 — Save State

For the selected sample, keep the existing state filenames and legacy matrix-display fields; write additional exploratory samples and their solver results under `supplementary/` instead. Preserve any previous selected sample before these writes. Add the coherent numerical sample, its provenance/checks, the initial-search record, and separate analytic statuses. The authoritative multiplier mapping is `named_dual_values`, with exactly the names in `constraint_metadata`; never infer missing active multipliers as zero. `lambda_matrix`/`lambda_groups` below are convenience displays for the returned object, not the inventory of all owners.

```python
assert numerical_certificate_verified and closed_form_search['completed']
for relative_path, expected_hash in source_hashes.items():
    assert hashlib.sha256((repo_root / relative_path).read_bytes()).hexdigest() == expected_hash
lambda_data = result.get_scalar_constraint_dual_value_in_numpy(obj)
def display_matrix(value):
    return dict(matrix=np.asarray(value.matrix, dtype=float).tolist(),
                row_names=list(value.row_names), col_names=list(value.col_names))
if isinstance(lambda_data, dict):
    lambda_display = {'lambda_groups': {str(name): display_matrix(value)
                                      for name, value in lambda_data.items()}}
else:
    primary = display_matrix(lambda_data)
    lambda_display = dict(lambda_matrix=primary['matrix'],
        lambda_row_names=primary['row_names'], lambda_col_names=primary['col_names'])
normalization = dict(tau_name=tau_name, initial_condition=b1['initial_condition'],
    performance_metric=b1['performance_metric'], bound_value=float(result.opt_value),
    bound_formula=b1['conjectured_rate'])
certificate_provenance = dict(solve_id=str(uuid.uuid4()), pep_type='primal',
    solver_status=str(result.solver_status), source_hashes=source_hashes,
    solver=dict(api='PEPBuilder.solve_primal', cvxpy_version=version('cvxpy'),
                effective_name='unavailable', settings={}))
state = {
    **b1, **lambda_display,
    'N': N_int, 'N_verify': N_int, 'opt_value': float(result.opt_value),
    'tau_sol': float(tau_sol), 'tau_name': tau_name,
    'relaxed_constraints': list(pb.relaxed_constraints),
    'S_matrix': S_array.tolist(), 'S_row_names': list(S_sol.row_names),
    'S_col_names': list(S_sol.col_names), 'basis_vectors': [str(v) for v in basis],
    'basis_scalars': [str(v) for v in ctx.basis_scalars()],
    'named_dual_values': named_dual_values, 'constraint_metadata': constraint_metadata,
    'normalization': normalization, 'certificate_provenance': certificate_provenance,
    'numerical_checks': numerical_checks, 'numerical_decomposition': numerical_decomposition,
    'closed_form_search': closed_form_search, 'formula_status': formula_status,
    'lamb_code': lamb_code, 'S_code': S_code,
    'S_decomp_type': 'ldl' if numerical_decomposition['method'] == 'reverse_ldl' else 'direct',
    'numerical_certificate_verified': numerical_certificate_verified,
    'analytic_full_pep_verified': analytic_full_pep_verified,
    'lyapunov_proof_verified': lyapunov_proof_verified,
    'require_analytic_full_pep': require_analytic_full_pep,
    'proof_valid': numerical_certificate_verified,  # Legacy numerical diagnostic only.
}
certificate_keys = (
    'N_verify', 'params_json', 'relaxed_constraints', 'S_matrix', 'S_row_names',
    'S_col_names', 'basis_vectors', 'basis_scalars', 'opt_value', 'tau_sol', 'tau_name',
    'named_dual_values', 'constraint_metadata', 'normalization', 'certificate_provenance',
    'numerical_checks', 'numerical_decomposition')
state['certificate_id'] = hashlib.sha256(json.dumps(
    {key: state[key] for key in certificate_keys}, sort_keys=True,
    separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()
for filename in ('{ALGO_NAME}_relaxed.json', '{ALGO_NAME}_b2.json'):
    (state_dir / filename).write_text(json.dumps(state, indent=2, allow_nan=False), encoding='utf-8')
print('State saved to', state_dir / '{ALGO_NAME}_b2.json')
```

Record effective solver details when actually exposed; `PEPResult` does not expose the chosen CVXPY solver name/options, so the example honestly marks that name unavailable rather than inventing it. Include all local mathematical dependencies in `source_hashes`. Capture them before solving and verify them again before saving. Retain additional analytic evidence and any explicit analytic-full-PEP user goal outside `certificate_keys`; formulas and final proof statuses may evolve without relabeling the fixed numerical sample.

`constraint_metadata[name]` contains `origin` (`initial`/`interpolation`), `owner` (`str(owner)` or null), actual `group` (or null), `kind` (`scalar`/`psd`), original `comparator` (`c.cmp.value`: `LE`, `GE`, `EQ`, `PEQ`, or `SEQ`), matrix `shape` (empty for scalar), and `relaxed`. Store the complete `D` and factor rows in `numerical_decomposition`; additional direct-piece data must also describe that same certificate. `formula_status` has `lambda` and `S` entries from `unresolved`, `candidate`, or `verified`; the last requires analytic-domain evidence, not a fit. `closed_form_search` records actual attempts, not planned work.

On a later invocation, rebuild the setup context without solving, validate the canonical `certificate_id`, source hashes, horizon/parameters/normalization, coordinate order, and complete constraint inventory, and recompute the numerical checks using the saved values. A hash or saved Boolean alone is not revalidation. If data are missing or stale, recover them from the original result/evidence or obtain one complete replacement certificate and invalidate/rebuild dependent partial sums and coefficients. Do not combine old lambda with newly solved S or extras. A legacy `proof_valid=True` is numerical evidence only; retain useful old formulas but recover and verify the missing numerical fields before numerical handoff.

---

## Step 8 — Update Lyapunov Notebook

Open the notebook created by Block 1 and update the proof-certificate sections. Follow the corresponding middle sections of `examples_peppy/_references/gd/gd_example_lyap.ipynb`.

Add or replace cells for:
- dense solve at `N_VERIFY`, with objective value, basis vectors, and compact summaries of active/nonzero entries in each lambda/function-class inequality group
- relaxation construction and preserved-optimum check
- relaxed certificate summaries, again focusing on active/nonzero entries and the preserved-optimum check rather than dumping all raw matrices
- nonzero relaxed lambda entries for every group, plus available closed-form candidates and their actual verification status; show labeled candidate matrices with `pf.pprint_labeled_matrix(...)` when available and state unresolved formulas explicitly
- the selected numerical S decomposition or available direct formula, including its labeled matrix and reconstruction check, with analytic status stated separately
- fixed-N numerical certificate identity checks for Gram, function-value, and constant components, including labeled residual matrices; retain a separate analytic full-PEP argument when established
- the brief initial closed-form search record and the unresolved components carried into numerical Lyapunov exploration

Keep the Block 1 setup and numerical-evidence cells intact unless they are wrong. The notebook should remain executable after this update, although later Lyapunov sections may still contain placeholder headings.

For notebook Markdown cells added or edited in this block, use `$...$` for inline math and `$$...$$` for display math. Verify their rendered appearance, not just their source delimiters, and record any unresolved rendering issue in the supplementary checklist.

If a separate file is created or reused to justify a proof condition in this block, include its relevant identity definitions, actual checks/results, and reasoning in the notebook under the [proof verification rule](../../plugins/peppy-workflow/references/output-layout.md#proof-verification-files-during-notebook-authoring). Reuse existing cells. Preserve the numerical handoff and explicit unresolved analytic status; this adds no earlier analytic-proof prerequisite.

Update the notebook's sibling `supplementary/<notebook-stem>_checklist.md` with this block's actual cell references, evidence, and unresolved requirements, following Block 1's Notebook Lifecycle. Inspect every notebook requirement listed above; future-block work stays pending. Keep the record out of the notebook and routine completion report, and disclose any unresolved requirement due in this block.

---

## Output

Report:
- The relaxed constraint set (which λ entries are active)
- Available lambda formulas/candidates and unresolved components from the initial closed-form attempt
- The S decomposition (LDL diagonal values and `ell` vectors, or direct formula)
- The separate numerical-certificate and analytic-full-PEP statuses; numerical verification is not a completed analytic proof
- Confirmation that the notebook was updated through the proof-certificate sections

**Next step**: `/lyap-define {ALGO_NAME}` once the numerical certificate and initial search are complete. Missing global closed forms do not block this default handoff. If an explicitly requested analytic full-PEP proof is still unresolved, say so and preserve that objective rather than claiming it complete.
