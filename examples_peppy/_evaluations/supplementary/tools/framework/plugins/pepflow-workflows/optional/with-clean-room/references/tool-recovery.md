# Clean-Room Tool Preparation and Recovery

**Audience:** Coordinator and worker. This is generic operational policy, safe to include with the worker packet; it contains no problem-specific answers or evaluation targets. Read it when preparing required checks or handling an actual tool/access incident. Apply the packet's frozen protocol if it is stricter; this file does not change a running evaluation's rules.

## Prepare the required route

Before target dispatch, review and freeze the tool adapter, executables/versions, Python environment, working directory, configuration, approved framework root, attempt-owned helper roots and writable cache locations. Use [the static-check adapter](../scripts/check_static.py) for required Ruff/ty checks; consult its command help for the supported interface and record the exact invocation. Include the reviewed adapter and this policy in the packet's permitted resources. Shared approved read-only sources are sufficient; no full workflow copy is required.

The adapter provides `preflight` for generic import/execution probes and `check` for explicit generated `.py`/`.ipynb` targets. Supply `--attempt-root`, the pinned absolute executable paths `--python`, `--ruff` and `--ty`, and a persistent `--evidence` JSON destination. Each `--approved-package` names a reviewed package directory itself, never a whole repository; each `--helper-root` names an attempt-owned helper directory. Declare `--framework-module` and `--dependency` for the generic probe. Preserve the reviewed per-attempt invocation/settings in the worker packet and use the same source/helper roots for the actual checks. Private staging is a tool-resolution control, not an OS sandbox.

Freeze the helper layout independently of those search roots: `--probe-helper-path` defaults to the attempt-relative `supplementary/runtime.py`. Supply the intended relative layout for other templates. The synthetic helper stays at that location even when a declared search root is wrong, so an unresolved helper fails preflight. The probe exercises generic imports only; actual notebook/setup checks and clean-kernel execution remain separate required gates.

Put explicit check targets after `--` and use a new supplementary evidence path for every invocation; previous evidence is immutable. Freeze the supported `ty` version with `--expect-ty-version` (the tested default is `0.0.82`). Exit codes are `0` for passed checks, `1` for genuine source diagnostics and `2` for operational/preflight failure; none asserts contamination. The per-command `--timeout` is not an attempt budget: the host must enforce the original overall deadline and cap operations by the remaining time.

Verify runtime and static analysis separately. A notebook's runtime `sys.path` mutation does not set a static analyzer's roots. Selecting a Python environment does not necessarily remove unwanted project roots. Do not infer a sealed boundary from `--project`, an extra search path, or a successful exit code. Use explicit supported configuration or an approved staging project, preserve notebook cell/source correspondence, and inspect the effective resolution evidence. Do not modify global configuration or frozen sources.

For a task requiring these checks, use the actual worker route on a small newly generated generic notebook/setup that imports an attempt-local helper in the intended layout, the approved framework and a normal installed dependency. Execute in a fresh kernel and run the required static checks. Also check an intentionally missing generic import to expose and inspect the diagnostic/search route; that expected failure is a preflight probe. Keep commands, versions, configuration, roots, return codes and runtime import locations. An arithmetic-only notebook is insufficient.

The adapter's separate synthetic regression checks should exclude inherited configuration and shadow modules outside approved roots; use invented generic fixtures, never existing proofs or other attempts. Test the shared adapter once, then validate each attempt's concrete paths through its actual worker route. If preparation fails, repair it before dispatch and record preparation separately. Check only tools needed by the requested task; unavailable system-wide access tracing is not a preflight prerequisite for declared instruction-only isolation.

## Classify evidence, not a label

Distinguish a configured search path, attempted access, successful read, and exposed/consumed content. Record what is observed and what is unknown.

| Observed event | Action |
| --- | --- |
| Ordinary lint/type error, unresolved local import, or generic repository path in a diagnostic, with no concrete evidence of prohibited-content consumption | Repair the permitted route/generated code and rerun the required check in the same attempt. Do not declare contamination from the error/path alone. |
| Access denied before prohibited content reached the worker or an output-influencing tool | Stop that route, inspect the already exposed metadata, then use an approved route if the metadata was harmless. A filename or error message that contains an answer is itself exposure. |
| Confirmed read of unapproved generic source/configuration | Record the boundary deviation. Continue only if the packet's predeclared narrow rule establishes permission and equivalence to an already reviewed resource. Preserve the deviation even then; never silently expand the allowlist. |
| Excluded proof, another condition's aid, evaluator material, sibling result or other prohibited mathematical information exposed to the worker or consumed by a tool influencing the attempt | Stop the affected attempt as `contaminated`, preserve evidence and the original slot, and claim no independent-success credit. |
| Concrete evidence of a possibly prohibited read or answer-bearing output that cannot yet be classified | Stop the suspect route and suspend mathematical work for bounded operational triage under the original clock. Resume only once the specific concern is resolved; otherwise record unresolved access eligibility (`eligible=false`) and the actual stop reason, not confirmed contamination. |
| Only the declared limitations of instruction-only isolation, such as unavailable exhaustive OS tracing | Continue with those limits recorded. This alone is not a new access incident or reason to stop. |

An equivalence rule must be fixed before dispatch and identify already reviewed resource identities/hashes, permitted alternate routes and required evidence. A matching package name/version or a worker's opinion that material is generic is insufficient. Without a qualifying rule, a confirmed unapproved read cannot be silently accepted. Resolve it through allowed operational evidence; do not open further excluded sources to justify it. No rule can excuse actual prohibited answer exposure.

For a concrete uncertain incident, use a short diagnostic plan limited to attempt-owned files, approved metadata and available access logs. Stop when the issue is resolved, no permitted diagnostic can resolve it, or the original deadline is reached; do not repeat inconclusive checks indefinitely. Ordinary instruction-only visibility gaps do not trigger this branch. A tool obstruction remains an operational outcome, separate from unfinished mathematical discovery.

## Recover within the existing attempt

1. Preserve the failed command, working directory, configuration, tool version, diagnostics and concrete access observations in the existing supplementary record.
2. Stop the failing/suspect route and choose an evidence-supported repair using only permitted resources. Do not search the repository for a replacement implementation or proof.
3. Repair attempt-owned configuration/helper roots, use the reviewed adapter, or correct ordinary errors in the worker's own generated imports/source. Keep frozen framework, skills, inputs, assistance, solver criteria, rank thresholds and proof tolerances unchanged. Do not suppress all diagnostics or skip a required gate.
4. If configuration changed, repeat the generic resolution probe; then repeat the original required check on the actual generated notebook/setup. Preserve both failure and recovery evidence. Required clean-kernel execution and static checks must still pass.
5. Continue the same session from the actual incomplete block. Charge recovery time/tokens to that block under the original accounting and deadline.

These reversible repairs are already authorized within the task's permissions; do not ask the user to approve them again. Prefer worker-side recovery from the fixed packet. Any permitted coordinator assistance stays operational under the existing continuation rules and contains no mathematical hint or evaluator feedback.

Recovery never resets the clock, supplies a fresh context, starts a replacement attempt, repeats the mathematical attempt from scratch, or changes the denominator of a registered experiment. Do not rerun an identical failed command without new evidence. An unrecoverable obstruction or unchanged deadline may still end execution; preserve the actual partial result and stop reason.

## Record and review independently

Reuse the task's existing events, preflight/access records and details, or its single supplementary clean-room record. Include attempt/block/time, command/configuration/roots, the distinction between attempted access and consumed content, classification, scoped repairs/outcome, evidence locations, original session/deadline, measured recovery cost, and remaining audit limits. Preserve access eligibility separately from mathematical/delivery status.

A later reviewer must assess the evidence rather than accept a `contaminated` label as conclusive. Conversely, a field saying no target content was observed does not alone prove eligibility. Keep the original declaration and stopped timeline in any later adjudication; a corrected access classification cannot invent completed work or turn an unfinished block into a proof. This policy authorizes no retrospective restart, score change or historical-record rewrite.
