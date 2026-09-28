---
name: localize-n-summation-proof
description: "Localize difficult positivity or nonvanishing arguments in an existing Peppy/PEPFlow proof using exact symbolic identities for generic indices. Use when requested or when a proof-relevant sign or symbolic-summation bottleneck warrants it; skip elementary signs and already concise valid arguments."
---

# Localize N-Summation Proof

Refine the sign argument for a selected coefficient, weight, pivot, or denominator in an existing PEP or Lyapunov candidate. Seek an arbitrary-horizon proof using scalar reasoning or a state whose dimension is independent of the horizon, with an exact symbolic audit of its local identities.

## Invocation and Scope

Accept the existing notebook path and an optional target coefficient or obligation:

```text
$localize-n-summation-proof <notebook-path> [target obligation]
```

Use the notebook identified in the current conversation when unambiguous; ask only if the target cannot be determined. Resolve relative paths from the invocation directory. Read the notebook's relevant definitions, proof, and supporting evidence, and follow the shared [output layout policy](../../references/output-layout.md).

This optional skill supports both explicit requests and agent-selected invocation within the current proof-construction or refinement task. Once the candidate and coefficient definitions exist, invoke when a plausible local reduction addresses one of these conditions:

- A required positivity, nonnegativity, or nonvanishing claim is a proof bottleneck, including a claim supported only by sampled values.
- A proof-critical sum or indexed identity can currently be checked only after concrete index or horizon substitution, and a generic symbolic verification is needed.
- A valid global sign argument has an identified source of complexity and a concrete recurrence, factorization, or invariant could materially simplify verification.

Skip autonomous invocation when the sign is irrelevant to the selected proof, a concise valid argument already suffices, or the user has disabled autonomous localization. A conjecture label or the mere presence of a sum or matrix does not warrant invocation. Do not search other experiments for unsolicited refinements. An explicit request may still target an already valid proof.

Briefly state the target obligation and reason for invoking the skill, then proceed within the existing task and resource budget without requiring a separate skill request. A scope restriction such as export-only, read-only review, or frozen evaluation prohibits proof revision unless that restriction is changed by the user; finding a gap there calls for reporting it.

Preserve the algorithm, theorem, rate, selected Lyapunov function, coefficient definitions, and certificate identities during localization. Justify any equivalent reparameterization and identify it with the original quantities. Do not strengthen assumptions, narrow the domain, restart coefficient discovery, or rerun Blocks 1-5. This preserves a selected candidate during refinement; the surrounding discovery workflow may still construct or solve for its own candidates.

## Identify the Actual Sign Obligations

Read where each proposed sign is used in the step inequality, square decomposition, or boundary argument. Inventory only the necessary claims, with their parameter and index domains. Distinguish strict positivity, nonnegativity, and nonzero denominators; not every coefficient must be positive.

Separate established certificate identities, imported analytic inequalities, and unresolved sign claims. State a noncircular justification or permitted source for each imported fact. A numerical certificate residual, solver status, stored proof flag, or a symbol declared `positive=True` does not prove a property of the original coefficient.

Respect the current task's source-access restrictions. Derive the invariant from this coefficient construction; do not borrow another example's invariant without showing why it applies.

## Construct a Local Argument

Prefer the simplest method that closes the actual obligation:

1. A direct scalar factorization or decomposition into quantities already proved nonnegative.
2. A strengthened scalar induction, using a sufficient bound or relation rather than the target sign alone.
3. A fixed-dimensional state with finitely many scalar invariants.

Inspect differences, recurrences, cancellations, and low-rank updates. Choose forward or backward induction according to the construction. Derive and justify a relation before using it to reduce a symbolic expression.

A scalar cumulative quantity maintained by a recurrence is allowed. A state containing the full history, or a horizon-sized determinant hidden behind a function call, is not fixed-dimensional. A fixed-dimensional matrix argument is allowed but must not be described as matrix-free. Numerical PEP solves and rank diagnostics outside this local sign kernel may still depend on the horizon.

Justify divisions and cancellations before using them. If a recurrence divides by the target quantity, establish the required sign or nonvanishing independently of that divided update, for example from an undivided identity and a valid inductive bound. Handle zero and degenerate cases instead of silently excluding them.

Identify every auxiliary quantity with its original coefficient or cumulative sum. Prove matching initialization and the generic transition, including reindexing and empty-sum conventions. Cover the opposite endpoint and exceptional small horizons. State how the invariants imply the required sign over the full claimed domain.

## Exact Verification with Generic Indices

Avoid proof representations whose essential algebraic identities can only be checked after substituting concrete integers for summation or iteration indices, summation limits, or the horizon. Keep these quantities symbolic over the claimed domain and verify the generic identities exactly in SymPy or an equivalent CAS.

A symbolic sum is acceptable when its needed identity can be checked exactly within the fixed-dimensional audit. Otherwise reduce it to a telescoping, recurrence, difference, or invariant identity. Do not replace the general check with horizon-by-horizon expansion, summand enumeration, or finite sweeps, even in exact rational arithmetic.

Construct the actual expressions and reduce their residuals exactly to zero using explicitly stated, justified relations. Audit invariant transport and identification with the original coefficients as well as the final local identity. Introducing an unconstrained symbol for a sum must not hide the identity that needed verification. Merely constructing an unevaluated `Eq` or `Sum`, assuming the target equality, or leaving an unresolved simplification is not a completed check.

Concrete substitutions are legitimate for initialization and genuinely exceptional small-index or degenerate cases. Generic endpoint identities must still retain the arbitrary horizon: `k = N` is a symbolic endpoint check when `N` stays symbolic. These special cases supplement the generic transition; they cannot replace it.

Explain the verification boundary. Analytic reasoning establishes domains, denominator conditions, sign assumptions, and the induction implication. CAS verifies the exact algebraic identities used in that argument. A zero residual alone is not a positivity proof. Keep finite-horizon and floating-point observations labeled as diagnostics.

## Notebook Deliverable

Update the relevant proof section of the same notebook. Keep the complete result reviewable there:

- Briefly identify the original bottleneck.
- State a lemma with its assumptions, parameter/index domain, and exact sign conclusion.
- Present the local argument, coefficient identification, invariant, and required initial, transition, endpoint, and exceptional cases.
- Include compact executable cells with the actual definitions, exact identity checks, and executed results, reusing existing notebook definitions.
- Explain how the analytic argument and verified identities discharge the obligation; cite the lemma at its use in the final inequality or telescoping argument. State any remaining gap.

An external verifier call or stored Boolean cannot replace the notebook's proof-critical calculations. Generic library APIs and the existing setup and workflow state remain allowed. Do not expand elementary sign facts or unrelated proofs merely because this skill is available.

Use `$...$` and `$$...$$` in notebook Markdown. Execute the new or changed audit cells, check clean-kernel reproducibility when feasible within the current task, and inspect the rendered mathematics. Reuse verified workflow state where supported; do not restart expensive PEP discovery solely to refine a sign argument. Preserve the owning block's normal final notebook checks, and report any execution or rendering check that remains unperformed.

Use existing evidence-checklist entries under `supplementary/` when the workflow keeps them. Do not create a separate proof report, notebook variant, PDF, TeX, or optional-workflow state by default. Keep unavoidable runtime files under the notebook's `supplementary/.runtime/`; other necessary supporting files follow the shared output policy. Do not create a `b6` file or a new state schema.

## Stopping and Workflow Handoff

Make a focused attempt on the available local structure. Stop when the proof closes or the attempted reductions fail to establish the needed invariant or generic identity, and report the specific unresolved obligation. Do not repeatedly invoke the skill on the same unchanged obstacle without new evidence or a materially different approach. Stay within the existing resource budget.

Distinguish three outcomes:

- **Localized:** The necessary sign has a complete local proof and the required exact generic checks.
- **Global proof retained:** An existing valid global proof remains valid, but localization is incomplete. Preserve that proof and report the unachieved refinement separately.
- **Sign unresolved:** No adequate analytic argument establishes a necessary sign. Numerical agreement or a missing invariant does not discharge it.

This is not a sixth block or a new analytic completion gate for numerical Blocks 3 and 4. With a valid numerical certificate and handoff, defer unresolved localization when appropriate and continue numerical exploration with accurate status. Block 5 must justify every sign actually needed for its final theorem before claiming a proved result. Do not require localization of unused global full-PEP coefficients or replace a valid global proof merely to satisfy this method.

Report the notebook section or cells changed, the affected obligation and outcome, and the verification performed or still pending. If localization fails, preserve established claims and distinguish the attempted refinement from the accepted proof.
