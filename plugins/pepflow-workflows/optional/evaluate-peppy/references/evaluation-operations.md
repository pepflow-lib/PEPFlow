# Evaluation operations

**Controller/evaluator only. Do not dispatch this document or its helper scripts to generation workers.**

**Campaign protocol:** `2026-09-20.isolation-recovery-v1`. **Presentation policy:** `evaluation-ancillary-v1`.

## Scope and compatibility

This protocol changes evaluation orchestration, observations and presentation policy. Preserve the evaluated branch's frozen mathematical skills, case inputs, unknown rates, PGM candidate-SOS assistance and proof targets. In particular, retain the baseline B1/B2 discovery and full-certificate checks, B3 rank constancy across at least two horizons, B4 reconstruction at every required index including endpoints, and B5 exact theorem obligations. Do not reinterpret supplied SOS as a newly enforced fixed-S constraint or introduce a different solver API. No `pepflow/` source changes are required or authorized by this evaluation.

Freeze the campaign protocol and presentation policy separately from framework and mathematical skill hashes. This version adds import/configuration preflight and evidence-based same-session recovery to the existing presentation policy. It applies to newly prepared campaigns; frozen historical protocols, submissions and verdicts retain their recorded versions. Any retrospective adjudication is separately dated and preserves the original timeline and evidence. Keep generation settings, assistance, resources and presentation policy comparable when timing workflow versions; disclose differences.

For the paper suite, let `C` be the selected nonempty condition list, `M=len(C)` and `K` the uniform positive repetition count. Register `M*K` attempts and `5*M*K` block records. Default to all six conditions and `K=5`; an explicit request to time one named condition defaults to `K=1`. Use `P=K` matched PGM pairs only when both PGM conditions are selected, otherwise `P=0` with null pair IDs and a not-applicable comparison. A separate suite may reuse the operational contracts below with its own frozen case manifest and counts; the paper targets and assistance do not transfer automatically.

## Generic preflight and source isolation

Before timed target dispatch, test required generic capabilities through the actual isolated worker tool route, using its pinned interpreter/kernel, working-directory rules, approved tools/configuration and private mutable caches. Use the worker-safe [static-check adapter](../scripts/check_static.py) in its `preflight` mode: exercise an attempt-local helper, the approved framework and an installed generic dependency in a newly generated notebook/setup, execute in a fresh pinned kernel, and run the required static checks. A deliberate missing generic import must expose the static analyzer's effective resolution roots; record its expected diagnostic separately from failures of the real checks. A version check or arithmetic-only notebook is insufficient. Verify actual `pepflow.__file__`, dependency versions, source roots and configuration against the approved snapshot. A host-only successful check does not establish worker access.

Prepare and hash the adapter, configuration choices and approved package/helper roots before dispatch; package only its worker-safe code and the [tool recovery policy](tool-recovery.md), never this controller reference. Pin actual tool executables. Keep transient staging and caches inside the attempt's private runtime, and keep commands, configuration/source hashes and diagnostic evidence in durable supplementary records. Read-only reviewed generic resources may be shared; no full workflow copy per invocation is required. Do not treat `--python`, `--project`, or an added search path alone as proof of isolation. The adapter's source/configuration checks do not establish OS-enforced read isolation.

Before adopting a new adapter/tool version, test parent configuration discovery and module shadowing with synthetic generic fixtures. No existing mathematical examples or sibling results may serve as canaries. Every attempt must pass its concrete preflight through the worker route before receiving target inputs. If preparation fails, repair the declared operational environment or report the actual obstruction; do not begin a timed attempt with a known broken import route.

Use an explicit, reviewed allowlist for generic framework files, mathematical skill bodies and their necessary transitive references. Inspect transitive imports and linked resources; keep target tests, solved notebooks, evaluator documents, controller helpers, other attempts and history inaccessible. An empty notebook skeleton may be created from generic prose, never by reading an excluded example. Use the adapter's bounded generic probes without importing existing example scaffolds or target-specific preparation scripts.

Keep the smoke result, command paths, versions, hashes and enforcement limitations in campaign supplementary evidence. Missing required mathematical/runtime capabilities are operational limitations to resolve or report before dispatch, not mathematical failures. Honor existing permission boundaries. Browser availability, image display, screenshots and visual inspection are never required preflight capabilities. Do not trigger new installations, approval requests or lengthy repairs solely for rendering. After-dispatch setup remains charged and disclosed.

Verify provider and narrowly scoped host usage sources, session-to-attempt mappings and request-boundary observation before declaring measurement unavailable. Expose no controller or sibling transcript to workers. Missing counters remain missing; they do not prevent a proof from passing.

## Tool incidents and recovery

Supply the [worker-safe recovery policy](tool-recovery.md) before dispatch. Ordinary lint/import/configuration failures and generic path diagnostics enter same-session repair; failed checks remain failed until corrected. Record actual blocked accesses, generic boundary deviations, concrete unresolved exposure and confirmed prohibited content separately. Instruction-only controls and nonexhaustive logs alone do not invalidate an attempt. Do not expand source permissions or add mathematical assistance in response to difficulty.

Freeze any permitted generic-resource equivalence exceptions in the manifest; the default permits no undeclared source substitution. The worker may repair its own generated imports and task-local configuration without repeated permission requests, rerun the preflight when resolution changes, and rerun the required checks on its real notebook/setup. All repair, audit and waiting time after dispatch stays on the original block/deadline; use the existing tooling-setup activity category when observed. No replacement worker, mathematical restart, clock reset, blanket diagnostic suppression, or source/gate modification is allowed.

For concrete unresolved access evidence, suspend mathematical work and perform bounded operational triage. If unresolved at stop, record `access_status=unresolved`, `eligible=false`, evidence and reason; use operational `error` or deadline-driven `timeout`, not an unsupported contamination claim. Confirmed prohibited exposure remains `contaminated`. The evaluator independently assesses access eligibility from evidence, preserving raw worker declarations, actual stopping and verdict history. A premature worker label cannot create evidence or recover work that was never done.

## Same-session continuation

After supplying the frozen operational settings at initial dispatch, the controller may relay only the fixed operational sentence:

```text
Proceed with the next step under the existing case instructions.
```

Where the host exposes a same-session API, use [continuation.py](../scripts/continuation.py) with a `send` callback bound to that API after an observed block handoff. Include the frozen `protocol_version` in the original attempt record. Preserve the attempt ID, session ID, original deadline and stable attempt/session/handoff idempotency key; persist receipts in host events. A revisit is part of the same attempt. Never add mathematical advice, evaluator feedback or another attempt's content.

The helper is an adapter, not a worker launcher, transport or independent timer. The callback must enforce the original deadline and host idempotency. After an uncertain send, inspect host receipts before retrying. Always supply the original frozen attempt record; the helper cannot authenticate a caller-modified deadline. With no supported adapter, record `unsupported` and use an existing permitted same-session mechanism. Do not replace the session or reset its budget. Freeze capability/enforcement limits before dispatch. Its `schema_version=same-session-continuation-v1` describes receipts separately from the campaign protocol.

## Orthogonal activity accounting

Retain B1-B5 visits, request attribution, generation time and review time. Add observable activity intervals to existing host/tool events without requiring an extra LLM journal or additional proof checks. Use these labels:

- `mathematical_discovery_validation`
- `notebook_authoring_revision`
- `execution_rendered_review`
- `tooling_setup_repair`
- `handoff_wait`
- `unallocated`

For this protocol, `execution_rendered_review` is a legacy key for required notebook execution only; ancillary rendering has separate post-generation records. Service/model waits stay with the active activity unless separately observable. Handoff wait means an observed host handoff-to-continuation/start interval, not inferred idle time.

Run the controller-only [collector](../scripts/collect_activity.py), passing the campaign's actual frozen version:

```text
python collect_activity.py EVENTS.jsonl --start DISPATCH_ISO --stop STOP_ISO --protocol-version 2026-09-20.isolation-recovery-v1 --output activity_timing.json
```

The generic function API may omit a protocol only for a non-campaign smoke; campaign records must carry their frozen version. `schema_version=activity-accounting-v1` identifies the helper schema independently.

Each `activity_interval` event has timezone-aware `start`/`end`, a known `activity`, and an `evidence_ref` to real observations. Adapt supported host events without inferring labels from block names or broad legacy milestones. Same-label parallel intervals use their union; conflicting overlaps and gaps become unallocated. Reversed and out-of-attempt intervals are errors. The collector partitions each elapsed instant once and reconciles `attempt_wall_seconds = sum(activity_seconds)` independently of the block view. Never add block totals, activity totals and tool wall times together.

Normalized `request_usage` events have stable `request_id`, `tokens` as a nonempty object of observed nonnegative integer provider-defined deltas, and `evidence_ref`. Assign activity only when `activity_boundary_observed=true`; otherwise use unallocated. Exact duplicate records are deduplicated; conflicting duplicates fail. Normalize cumulative counters upstream with baseline/reset checks. Counter fields may overlap, including cached input or reasoning; never sum them into an invented total. The collector returns `tokens_total=null` with partial/unavailable coverage; merge complete totals only after separate host coverage reconciliation. Preserve block attribution independently and missing fields honestly.

Save controller-derived activity records at campaign-level `supplementary/measurements/<attempt_id>/activity_timing.json` and reference them from `details.json`. Keep these records and raw controller/host usage logs outside worker-readable paths; workers only write their own operational handoff evidence. Neither collection nor reporting exposes sibling events or controller transcripts to generation. Keep solver horizons/statuses/durations, recovery reasons, revisits, unexpected setup and verification events when observed; do not infer hidden work from broad timing windows. Present `timing.md` separately from compact PASS/FAIL results, linking readable durations to canonical seconds and token coverage. Record preparation, generation, independent review, ancillary rendering, requested visual/export work and end-to-end elapsed separately. Concurrent attempt totals are not campaign elapsed time.

## Evaluation-only rendering override

Apply this presentation policy in worker instructions and assessment, even when the frozen ordinary skills require rendered or visual review. It overrides presentation-related gates only during this evaluation. It does not change mathematical calculations, required notebook content, source checks that affect execution or formulas, clean-kernel execution, full-certificate checks, rank/reconstruction requirements or theorem verification. Keep a record of the override rather than editing the frozen mathematical skills.

Default generation performs no browser launch, screenshots or model image inspection. Check Markdown math delimiters and suspicious escapes as inexpensive source diagnostics while retaining required mathematical and execution checks. Presentation-only warnings do not stop dispatch, block transitions, finalization or reporting and do not make any block, delivery or final verdict fail. Record genuine invalid identities, missing proof content and execution failures under their original gates. Do not treat a saved `rendering unavailable` message as a mathematical failure; do not ignore a mixed note that also reports an unverified boundary identity.

Ancillary automated rendering is optional, after all selected generation submissions are frozen, and only through an already permitted, available bounded route using saved outputs. It must not delay independent review or the result report. Use a separate default 30-second per-notebook cap, no installation, approval wait or repair solely for rendering, and no notebook re-execution or proof changes. With no suitable route, skip it. Preserve an actual `checked`, `partial`, `unavailable`, `timed_out` or `skipped` result and evidence only if a diagnostic is attempted or useful; absence of a rendering report is not a missing delivery requirement. A source-only check is not an actual rendered result.

Visual inspection is available only when the user separately requests it, after independent assessment. Treat it as separate work and costs; do not alter frozen submissions or silently revise an experiment verdict. Requested PDF/TeX export still follows its own optional skill and validation requirements after assessment. Keep rendering/export issues separate from the submitted proof's mathematical verdict, preserving review history if a new mathematical gap is identified.
