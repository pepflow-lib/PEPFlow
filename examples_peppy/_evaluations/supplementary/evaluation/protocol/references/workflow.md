# Evaluate Peppy: Campaign Workflow

**Audience:** Controller and evaluator. Reusable execution instructions. Creating or reviewing this document does not start an experiment or implement a runner. This full document is for the controller and evaluator, not for generation workers.

## 1. Objective and scope

This protocol is `2026-09-20.isolation-recovery-v1`. It adds import/configuration preflight and evidence-based operational recovery while preserving the frozen mathematical Block 1-5 workflow and `evaluation-ancillary-v1` presentation policy. Read [evaluation operations](evaluation-operations.md) for scope, runtime checks, accounting and the evaluation-only rendering override. It does not introduce a new supplied-multiplier route, change the rank gate, or defer required endpoint reconstruction. Use this version for newly prepared campaigns; do not change protocols or rescore frozen historical runs implicitly.

The available suite has six conditions covering five paper algorithms. Freeze a nonempty selected list `C`, use `M = len(C)`, and run each selected condition `K = repetitions` times in fresh discovery sessions. Default to all six conditions and `K=5`; an explicit request to time one named condition defaults to `K=1`. This produces `M * K` planned attempts and `5 * M * K` Block 1-5 records (30 and 150 for the default full suite) under suite ID `paper-five-pgm-sos-v2`; it is not the separate conjecture suite. Let `P=K` when both PGM conditions are selected, otherwise `P=0`. The table lists available conditions, not an instruction to add unselected attempts.

| case_id | condition_id | Assistance | Repetitions |
| --- | --- | --- | --- |
| pgm | pgm_with_sos | Existing fixed candidate SOS decomposition | K |
| pgm | pgm_without_sos | None | K |
| ogm | ogm | None | K |
| bppm | bppm | Supplied conjectured rate | K |
| feg | feg | None | K |
| dual_feg | dual_feg | None | K |

Number repetitions from 1 through `K`, using IDs `r01`, `r02`, and so on, with at least two digits (`r100` is valid). Use `attempt_id=<condition_id>_<repetition_id>`, for example `pgm_without_sos_r01`. When both PGM conditions are selected, assign their attempts in each round a shared `pair_id=pgm_<repetition_id>`; otherwise use null, including an unpaired selected PGM condition. Use null for non-PGM conditions. A pair matches the round and controlled execution settings, not a shared model trajectory or conversation. Both PGM conditions have identical problem inputs and an unknown conjectured rate; only `pgm_with_sos` receives the existing fixed candidate decomposition. `pgm_without_sos` may discover and use an SOS decomposition itself. Freeze that aid before dispatch; do not substitute a decomposition discovered in another attempt.

For every attempt, record:

- Time and token usage for each block and for the complete attempt, including revisits.
- A pass/fail summary for every block and the final mathematical result.
- Brief reasons and inspectable evidence behind every judgment.

Final mathematical success means that the submitted Lyapunov argument proves the target convergence guarantee. Its potential, basis, and SOS decomposition may differ from the paper. Matching only the asymptotic order is insufficient: preserve the assumptions, performance metric, finite-horizon constant, parameter normalization, and horizon range. A stronger proved guarantee that implies the target also qualifies.

Use the sibling references as the canonical protocol resources:

- [Case inputs](case-inputs.md): common assumptions, individual algorithm packets and the declared PGM aid.
- [Worker protocol](worker-protocol.md): the generation-only Block 1-5 procedure, recovery and measurement handoffs.
- [Clean-room policy](clean-room.md): information access and isolation requirements.
- [Evaluation rubric](evaluation-rubric.md): controller/evaluator-only targets and block/final judgments.
- [Evaluation operations](evaluation-operations.md): controller/evaluator-only runtime checks, accounting helpers and evaluation presentation policy.

This document specifies repetition, orchestration, measurement and reporting. It is controller/evaluator material; send only the allowlisted extracts described below to generation workers. Record underlying statuses in supplementary files even though the summary is binary. Run one uninterrupted attempt for each of the `M * K` preregistered `(condition, repetition)` slots.

This is an opt-in AI experiment, separate from ordinary pytest and routine CI. Do not modify the `pepflow/` source or active skills to execute it. It is independent of any particular AI provider or orchestration application.

## 2. Invocation and defaults

Use the configuration and invocation rules in [the optional skill](../SKILL.md). A minimal request is:

```text
Use evaluate-peppy with GPT-6 Astra and medium reasoning for generation and evaluation.
```

This is an example, not a fixed model default. Ask for the generation model and supported inference settings only when missing. Use those same settings for evaluation unless the user specifies different ones. Use one independent review session per submission, with the same per-submission wall-time cap as generation and no review token cap unless overridden; unresolved validity at that limit remains REVIEW. Freeze the review procedure and review budget before dispatch, and announce the resolved defaults rather than requesting every setting from the user. Do not require a provider-specific skill syntax: reading and following the skill files is an equivalent invocation.

Resolve `conditions` from explicit IDs or an unambiguous natural-language selection; default to all six and clarify ambiguous choices rather than guessing the PGM assistance condition. Reject empty, duplicate or unknown IDs. Resolve `repetitions` from an explicit positive integer or an unambiguous natural-language count; default to 5, except an explicit request to time one named condition defaults to 1. Clarify invalid or ambiguous counts before dispatch. Apply the same count to every selected condition, freeze `C` and `K`, and derive `K` rounds, `M * K` attempts, `5 * M * K` block rows and `P` PGM pairs. Unselected conditions are not failed or unstarted attempts. Do not stop early after successes, extend the count after failures, or fill a smaller requested campaign to five repetitions. Repetition count and concurrency are independent.

Use `K` sequential rounds with default parallel execution using up to five available workers in each round, 120 minutes per attempt, no token cap, the active recovery policy through N=12, and no PDF/TeX export. Save outputs under `examples_peppy/_evaluations/`, relative to the evaluated repository root, not the installed plugin directory. Honor explicit pre-dispatch overrides and record them. Keep model and reasoning settings fixed across both PGM conditions and all repetitions; an adaptive reasoning-escalation pilot is a separate design, not a recovery action in this campaign.

For `parallel`, resolve the worker limit before dispatch as the smaller of five, `M` and available worker capacity, excluding the controller and respecting any user-specified cap. Announce and record this limit, then proceed without requesting approval solely because fewer than five workers are available. Preregister each round's queue by restricting `pgm_with_sos, pgm_without_sos, ogm, bppm, feg, dual_feg` to `C`. When both PGM conditions are selected, they occupy the first two positions. Before any dispatch, randomize their pair order across the `K` rounds: for even `K`, each condition is first in `K/2` rounds; for odd `K`, assign the extra first position randomly so the counts are `floor(K/2)` and `ceil(K/2)`. With `K=1`, randomize the single pair. When no pair exists, retain the selected base queue and record pair randomization as not applicable. Record the realized queues and randomization method for every campaign. Start as many conditions as fit, then start the next queued condition as soon as a slot becomes free. Do not wait for a whole batch to finish before filling a free slot. Finish every selected condition before starting the next round. If only one worker is available, disclose and record that attempts will not overlap; the same queue policy still applies.

An ordinary request to run the five examples in parallel selects this policy. If the user explicitly makes an exact simultaneous-worker count mandatory and the host cannot provide it, resolve that constraint before dispatch. If no worker or fresh independent context is available, report the missing capability. If the user explicitly selects `sequential`, use the same preregistered per-round condition queues with one worker at a time and record that variant. Generation uses one primary worker per attempt, with no additional generation agents. Worker capacity never changes the planned `M * K` attempts, model settings, per-attempt budgets, or assessment criteria.

## 3. Freeze settings and prepare the campaign

Create a new `campaign_id=<UTC_timestamp>_paper5_pgm_sos_6x<K>_isolation1` for the full suite, or `<UTC_timestamp>_<condition-or-subset>_<M>x<K>_isolation1` for a subset. Record the full protocol separately; a directory suffix or the suite ID is not a protocol version. Register all `M * K` selected slots before the first dispatch. Previous pilot attempts, including earlier PGM runs, are not registered repetitions of this campaign. Do not overwrite existing results, import past successes, replace failed slots, or select the best of several unregistered attempts.

Record in `supplementary/manifest.json`:

- `protocol_version=2026-09-20.isolation-recovery-v1`, protocol/resource/helper hashes, requested selection and repetition count (null when omitted), resolved selected `C`, `M`, `repetitions=K`, planned `M*K` attempts, `5*M*K` block rows and `P` pairs, case/condition/pair IDs and repetition IDs for 1 through `K`. Record `presentation_policy=evaluation-ancillary-v1` separately from the frozen mathematical skill hashes.
- Framework revision and actual source hashes, including dirty contents; active skill/resource hashes; `pyproject.toml` and `uv.lock` hashes.
- Exact input packet, permitted aid, and evaluator-target hashes. Keep evaluator materials inaccessible to workers.
- Requested and observed model/inference settings, provider/runtime versions, and seed behavior where supported; do not invent unavailable observations or equivalent reasoning levels.
- Solver versions, fallback policy, accuracy settings, numerical/rank tolerances, resource/thread limits, and horizon policy.
- Requested execution mode, any mandatory exact concurrency, available worker capacity excluding the controller, resolved worker limit, preregistered per-round condition queues, PGM order randomization (or not applicable) and selected-condition round barrier; record observed concurrency and capacity changes with their timestamps in the supplementary records.
- Independent context/runtime mechanism, access restrictions, deadline mechanism, and measurement capabilities.
- Reviewed static-check adapter/version, pinned tool executables, allowed framework/helper roots, configuration, and each worker's import/configuration preflight evidence. Freeze any narrow generic-resource equivalence exception; otherwise no undeclared source substitution is permitted.
- Evaluation procedure, reviewer/model settings, review budget and any human adjudication policy, fixed uniformly before outcomes are known.

Use the current local skill instructions as the tested workflow. Freeze their actual contents for the campaign; do not fetch a different version mid-run. Verify the actual imported `pepflow.__file__` points to the worker's approved source snapshot.

Prepare the same required solver, notebook execution and static-check dependencies for all selected conditions before starting attempt clocks. Perform a generic non-target smoke check through the actual isolated worker tool route under its pinned Python/kernel, approved working directories, configuration and private writable caches. Follow [evaluation operations](evaluation-operations.md#generic-preflight-and-source-isolation) and the reviewed [static-check adapter](../../with-clean-room/scripts/check_static.py): exercise the real helper-import layout, approved framework and installed dependency in a fresh kernel and static checks, including a deliberately missing generic import to reveal effective resolution roots. A tool version or arithmetic-only notebook is insufficient. Verify the actual imported framework path, configuration, versions, runtime capabilities and time/token collector; host prewarming alone is insufficient. Freeze commands, outputs and hashes under controller supplementary evidence. Keep common tools read-only. Rendering/browser/image availability is not a dispatch prerequisite; do not install or repair rendering tools for preflight. Unexpected required-tool setup or resource differences after dispatch remain charged and disclosed. Do not solve any target or bypass permission boundaries during preflight.

Check both provider responses and accessible host session/usage logs before declaring tokens unavailable. Agent-tool responses without usage fields do not establish absence of host counters. The controller's collector may read narrowly scoped session identifiers, usage events and turn boundaries; it must not expose transcripts or other attempts' content to workers. Establish session-to-attempt and turn-to-block mappings before dispatch and retain them through every revisit. If complete counters remain unavailable, record exactly which sources were checked and the missing scope; do not estimate usage. Report missing capabilities before generation. An unavailable token counter does not make a mathematical proof fail.

Keep the model/reasoning, source/skills, solver and fallback settings, horizon limit, verification criteria, time budget and resource allocations identical between PGM conditions. Record actual concurrency, installation deviations and cache counters so timing and token differences can be interpreted. Independent fresh contexts and forbidden cross-condition access still apply to paired attempts.

The default 120-minute limit starts when the case prompt is dispatched into an available worker slot. Time waiting in the controller's case queue before dispatch is recorded separately and excluded from the attempt budget. After dispatch, the limit covers the complete attempt, including model/service waits, tools, solver calls, debugging, recovery, and the worker's own verification and notebook finalization. Enforce it with a host-side timer where available and record whether enforcement is technical or instruction-only. Do not extend budgets in response to progress. Any supported token cap is fixed before dispatch and its scope is recorded; a prompt alone does not enforce a cap.

Start the structural search at the active skill's initial `N_verify`, normally 4 or 6, and follow its recovery policy through 12 within the attempt budget. This campaign predeclares no exploration above 12 unless the user authorizes a different common range before dispatch. Apply the frozen limit during every worker recovery: after authorized recovery is exhausted, stop as `stopped_at_horizon_limit`; if the deadline arrives first, use `timeout`. Do not request an extension during this campaign. Confirm useful patterns early instead of requiring every horizon. A solve failure at 12 is not evidence that a usable rank profile at 12 was tested.

## 4. Clean-room generation

Read and apply [clean-room.md](clean-room.md) when preparing inputs and monitoring generation. The controller prepares packets and later collects outputs; it must not generate a proof in its own answer-bearing conversation.

Each worker receives only:

1. [worker-protocol.md](worker-protocol.md), [clean-room.md](clean-room.md), and the worker-safe [tool recovery policy](../../with-clean-room/references/tool-recovery.md).
2. The common assumptions, its own case subsection and its selected PGM condition notice when applicable from [case-inputs.md](case-inputs.md), plus the fixed SOS aid only for `pgm_with_sos`. The `pgm_without_sos` packet must omit that aid and all links or readable paths to it. Do not provide the full multi-case file or controller provenance.
3. Approved generic framework source, the frozen mathematical Block 1-5 skills, required generic references such as `references/output-layout.md`, the worker-safe static-check adapter and its resolved configuration, dependencies and documentation. Inspect and hash transitive resources and imports individually; do not wildcard-copy scripts or tests. Expose the adapter and approved resources through exact allowlisted paths or selective copies, not the whole controller skill. An empty presentation skeleton must be newly created from the generic notebook requirements, never extracted from a solved notebook.
4. Its resolved model/budget/resource settings, frozen horizon policy, output destination, approved file list, and host measurement instructions containing no target answers.

The entire evaluate-peppy skill, this controller workflow, the evaluation rubric, `evaluation-operations.md`, controller scripts and aggregate outputs are excluded from worker inputs and readable paths. Copy approved generic skills selectively; an unrestricted plugin copy would expose evaluator answers. Preserve the mathematical workflow while removing access to target-specific examples. In a worker's initial context or allowlist, do not include controller conversations, inherited memories, papers, historical results, or other attempts.

Create independent contexts and minimal workspaces with separate Python/Jupyter kernels, mutable solver state, temporary directories and writable caches. Reusing a worker slot for another case or repetition requires a fresh context and isolated workspace; do not continue the previous attempt's conversation or carry over its generated files or mutable runtime state. Filesystem restrictions should enforce the approved paths where possible; record instruction-only isolation when that is all the host provides. Keep the campaign-level supplementary directory and other attempt directories inaccessible to workers. Audit supplied instructions and linked generic resources as well as files directly copied into the workspace.

Use the declared PGM aid only in `pgm_with_sos` and the supplied rate only in BPPM; leave the other input unknowns unknown. Freeze packet and aid hashes before dispatch. Keep an access audit. Recover ordinary tool/import/configuration errors within the same session, block and deadline as specified in the clean-room policy; a failed check or generic path diagnostic alone is not contamination. Stop confirmed prohibited exposure without replacement, and record concrete unresolved access incidents separately. Do not waive gates or expand source permissions during recovery.

The controller supplies frozen operational settings at initial dispatch; subsequent continuation messages contain only `Proceed with the next step under the existing case instructions.` It must not supply mathematical hints, repair a proof, or relay evaluator feedback. Freeze submissions at each attempt's stop; wait until all selected generation slots have stopped before mathematical evaluation, ancillary rendering or optional export. Use the same-session continuation contract in [evaluation operations](evaluation-operations.md); it relays only the fixed sentence, preserves the original session/deadline and records host receipts. No host API support means the helper is unsupported, not permission to create replacement sessions.

## 5. Time and token accounting

Measure from real host events. Record UTC timestamps for audit and monotonic elapsed time where available. Persist per-visit and per-request events as work happens under each attempt's `supplementary/`, rather than reconstructing costs from notebook execution counters or recollection.

### Time

- `attempt_wall_seconds` runs from prompt dispatch into an available worker slot to completion or forced stop. Preparation and controller-queue waiting before dispatch are separate; exclude them from B1-B5 time and the attempt deadline. Model/service and resource waits after dispatch remain charged.
- Record when each condition attempt enters its round's queue, its actual dispatch and stop timestamps, dispatch order, and pre-dispatch `queue_wait_seconds`. Use dispatch/stop events to record observed worker concurrency over time and its peak; record unavailable observations explicitly. Queue waiting contributes to campaign elapsed time, not summed attempt time.
- Record every contiguous block visit with `block_id`, `visit_id`, start/end, elapsed seconds, and entry/exit reason. Sum all visits to obtain each block's `wall_seconds`.
- Keep only one active block label per attempt at a time. Charge tool execution, model/service waiting, and ordinary handoff waits to that active block. Initial dispatch starts B1; final notebook verification belongs to B5. Change the label before the next request or tool operation begins.
- For example, a B3 recovery returning to B2 charges the new certificate solve to B2, then resumed grouping to B3. If a new certificate invalidates B4 work, include the new B4 visit and require its checks again. Never reset the attempt clock.
- Overlapping tools inside a block do not create additive wall time: use the enclosing interval, not the sum of tool runtimes. If a transition was not observable, retain an unallocated interval rather than guessing.
- Reconcile `attempt_wall_seconds = sum(B1..B5 wall_seconds) + unallocated_seconds` within the recorded timer resolution. Missing measurements remain missing; unallocated time is visible in supplementary records.
- Separately record evaluation, controller/preparation, optional ancillary rendering and requested visual/export time. Also record campaign elapsed wall time. The sum of concurrent attempt times is not campaign elapsed time.

### Activity accounting and readable timing

Use the controller-only [evaluation operations](evaluation-operations.md) accounting contract to retain a second, non-additive view of observed activity intervals. Record controller-owned `supplementary/measurements/<attempt_id>/activity_timing.json` at campaign level, referenced from `details.json`; keep B1-B5 attribution independently. The collector's schema is separate from the frozen campaign `protocol_version`. Do not infer labels from block names, estimate missing intervals or add activity totals to block totals.

Provide `timing.md` beside `results.md` with readable B1-B5, generation total, independent review, preparation and campaign elapsed durations, observed token totals/coverage and links to canonical numeric records. Show unallocated time and unavailable measurements explicitly. Generation, review, ancillary rendering and requested exports have separate costs. Never subtract historical rendering costs or change old verdicts under this new policy.

### Tokens

- Use provider/host usage counters and stable request IDs when available. Otherwise retain stable host event identities, session IDs and turn IDs, and disclose the missing API request identifiers. Record usage once with its condition/attempt, active block/visit, source and exposed fields. Host-native usage events or local rollout counters are valid sources even when agent-tool replies omit usage.
- Align block transitions with request boundaries. Do not start substantive work on the next block in the same model request. A request that nevertheless spans blocks needs provider-supported attribution or an `unallocated` label; do not split counts by response length or elapsed time.
- Count input and output tokens for every request, including repeated context and provider-reported usage for retries. Include reasoning tokens only according to the provider's accounting: they may already be included in output tokens. Cached-input tokens may be a subset of input tokens. Preserve these fields without double-counting them.
- Document the provider-specific definition of `total_tokens`. For cumulative counters, establish the baseline, ignore repeated snapshots, detect resets or inherited usage, and reconcile valid deltas with the final total. Match deltas to actual session/turn boundaries for block attribution. Preserve the filtered usage evidence and any post-hoc correction history. Do not add cumulative session counters repeatedly or substitute character counts, estimated tokens, currency cost, or an invented reasoning-token figure.
- Sum all visits and requests for a block, including debugging, retries, and verification. Sum generation usage for the attempt separately from post-generation evaluation, controller, automatic approval/helper models, and export usage; state the scope of every total.
- When complete comparable counters exist, reconcile the attempt total against the five block totals plus unallocated usage. A known attempt total may coexist with unavailable block attribution; say so explicitly.
- For each scope, store `tokens_total`, `tokens_observed`, `usage_status` (`complete`, `partial`, or `unavailable`), and the usage definition/source. Set `tokens_total=null` when its complete total is unknown. A partial observed sum is not a complete total.

For a genuinely unreached block, zero time/usage is valid only when complete event coverage establishes that no work occurred; otherwise use null. Do not treat missing or unobservable usage as zero. Exclude assessment and export costs from the generation totals requested for B1-5, while retaining their separate costs.

## 6. Assessment

Before dispatch, freeze [evaluation-rubric.md](evaluation-rubric.md), its exact targets, the applicable active-skill tolerances, and the common reviewer procedure. After all generation has stopped, evaluate each frozen submission independently under that rubric. It contains the B1-B5 checks and the separate final mathematical judgment; do not send it to workers.

Block judgments concern the final coherent evidence after any revisits. Numerical handoffs in B2 and B4 remain allowed. Final mathematical PASS requires a submitted Lyapunov argument with valid identities, signs and base/terminal implications for the exact target rate; it does not require an identical potential or perfect notebook presentation. Preserve the underlying gate and mathematical verdicts, operational failures, contamination and unresolved review, then derive the binary summary below.

Review access eligibility from evidence under the frozen rubric, including observed reads/exposure, operational repairs and any predeclared generic-source exception. A worker's terminal label alone is insufficient. Keep raw declarations and the real stopped/completed history, even when their interpretation is corrected. Concrete unresolved access eligibility is distinct from both confirmed contamination and mathematical `REVIEW`; routine instruction-only observability limits do not establish ineligibility.

## 7. Binary summary and supplementary details

The user-facing `results.md` contains campaign identification, the two-sentence legend below, and one table with `M * K` rows. Each row identifies a condition and repetition and shows B1-B5 and Final using only linked `PASS` or `FAIL` labels. Do not put residuals, time, tokens, logs, or long explanations in this summary.

> PASS means that the corresponding requirement was established in a valid independent attempt. FAIL means that success was not established under this protocol; the linked detail distinguishes mathematical failure, incomplete review, unreached blocks, contamination, and infrastructure problems.

For blocks, display PASS only when `gate_verdict=PASS` and the attempt is eligible under the clean-room policy. For Final, display PASS only when `mathematical_verdict=PASS` and the attempt is eligible. Map all other underlying outcomes to display FAIL while retaining their true status and reason in supplementary files. Never label contaminated work a valid independent PASS. For a contaminated run, any earlier provisional check observations remain in the history only.

| Example / condition | Repetition | B1 | B2 | B3 | B4 | B5 | Final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PGM (supplied SOS) | r01 | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| PGM (no supplied SOS) | r01 | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |

These rows illustrate the shape only. Replace them with all `M * K` actual rows; do not fabricate results or leave placeholders. Label BPPM as receiving its conjectured rate, and preserve the other cases' assistance status in the manifest. Link each verdict to its block/final section in a concise assessment note.

```text
examples_peppy/_evaluations/<campaign_id>/
  results.md
  timing.md                         # readable costs, separate from binary verdicts
  supplementary/
    manifest.json
    details.json
    runs.csv
    blocks.csv
    pgm-sos-comparison.md            # P pairs, or an explicit not-applicable note
    measurements/                   # controller-only per-attempt derived accounting
      <attempt_id>/activity_timing.json
    assessments/
      pgm_with_sos_r01.md
      pgm_without_sos_r01.md
      ...                           # one brief note per planned attempt
    inputs/                         # frozen allowed worker packets
    evaluation/                     # evaluator-only targets, logs and validation copies
  pgm_with_sos/
    r01/
      pgm_setup.py
      pgm_example_lyap.ipynb
      state/                        # only actual b1-b5 and required certificate artifacts
      supplementary/
        events.jsonl                # timestamped visits/request usage/stop events
        access_audit.json
        ...                         # proof helpers and supporting evidence
    ...                             # additional repetitions only through K
  pgm_without_sos/                   # same pgm setup/notebook names, fresh attempts
    r01/                            # same per-attempt layout
    ...                             # additional repetitions only through K
  ogm/ ... bppm/ ... feg/ ... dual_feg/
```

The layout is campaign / condition / repetition: the tree illustrates available conditions; create only selected condition directories and configured repetition directories for actual work. For `K=1`, each condition has only `r01/`; for `K=2`, use `r01/` and `r02/`. Do not rename or migrate past campaign folders when the count changes.

Workers have access only to their own attempt directory and approved generic inputs. The campaign root `supplementary/` is controller/evaluator-owned and must not be worker-readable. The nested condition folders are output destinations, not permission to read the other PGM condition or sibling repetitions. Preserve `<case>` setup/notebook/state naming inside each condition/repetition directory; both PGM conditions use `pgm_setup.py`, `pgm_example_lyap.ipynb` and the existing PGM state schemas. Preserve existing block schemas, and make setup/state/helper paths resolve from each selected attempt directory. Keep the normal diagnostic notebook, not only a final theorem. Do not fabricate notebooks or state for unstarted/unreached work; their assessment rows still exist.

Use `details.json` as the canonical structured assessment record. Derive the CSVs, brief notes, and Markdown table from it to prevent inconsistent verdicts. Reference raw events and notebook cells instead of duplicating complete notebooks or transcripts.

Required CSV columns, with one row per planned attempt in `runs.csv` (`M * K` rows):

```csv
campaign_id,protocol_version,attempt_id,case_id,condition_id,pair_id,repetition,session_id,assistance,started,eligible,run_status,stop_reason,summary_result,mathematical_verdict,attempt_wall_seconds,block_wall_seconds_sum,unallocated_seconds,generation_tokens_total,generation_tokens_observed,usage_status,block_tokens_sum,unallocated_tokens,evaluation_wall_seconds,evaluation_tokens_total,evaluation_usage_status,workflow_complete,notebook_path,assessment_path
```

Required CSV columns, with one row per planned attempt and block in `blocks.csv` (`5 * M * K` rows):

```csv
campaign_id,protocol_version,attempt_id,case_id,condition_id,pair_id,repetition,block_id,reached,visit_count,gate_verdict,summary_result,mathematical_checks_passed,delivery_checks_passed,wall_seconds,tokens_total,tokens_observed,usage_status,required_checks,passed_checks,failure_code,assessment_path,evidence_refs
```

`block_tokens_sum` and `unallocated_tokens` denote complete attributed and complete unallocated generation totals, respectively. Set either to null when its coverage is incomplete; preserve observed subtotals and their coverage separately in `details.json`. Apply the same completeness rule to `block_wall_seconds_sum` and `unallocated_seconds`; a known total with unknown allocation does not justify invented block values.

Use `null` in JSON and empty numeric CSV fields for unknown or inapplicable measurements, with an explicit status/reason. Store boolean fields consistently; unknown checks are null, not false. Use seconds and raw token counts as canonical units. Each row is keyed by stable IDs; quote CSV fields correctly and use UTF-8.

`details.json` must retain, per attempt and block:

- Case/condition/pair identifiers; supplied-versus-discovered aid provenance and hashes; underlying and display verdicts, eligibility, operational state, stop reasons, first completion/final validity and revisit history.
- Queue-entry, dispatch and stop timestamps, dispatch order, pre-dispatch queue waiting, original frozen deadline, continuation receipt references and references to the campaign concurrency history.
- Activity accounting evidence/coverage, collector schema and campaign protocol version, generic worker preflight evidence, presentation policy and any separately attempted rendering diagnostics/costs.
- Per-visit timing and request/host-event usage references, actual input/cached-input/output/reasoning counters and accounting definitions, coverage/missingness, reconciliation outcomes, and attribution limitations.
- Named required checks with outcome, tolerance/domain, measured result, and evidence reference; counts alone are insufficient. Proof-obligation counts describe progress, not a substitute for final proof validity.
- B2 certificate identity and sign/reconstruction evidence; B3 per-horizon recipes/ranks/coverage; B4 per-index basis and complete-potential reconstruction evidence; B5 step/base/boundary and sign/rate judgments.
- Final target and scope comparison, exact proof section/cell references, and whether each verification was replayed or only inspected.
- Source/submission hashes, access-audit findings, review history, and paths to actual notebooks/states/evidence.
- Within the existing access audit: `access_status` (`no_incident`, `recovered`, `deviation`, `unresolved`, or `contaminated`), `eligible`, decision/evidence references, observed incident kinds, repairs and check outcomes, applicable frozen exceptions, and remaining audit limitations. Keep original worker labels separately; never infer actual exposure solely from a label or search-root string.

Each `assessments/<attempt_id>.md` should be short: one sentence explaining the final result, then one section per block with its status, time/tokens, a brief reason, and evidence links. Add a `Final` section identifying the submitted rate, the decisive proof checks, and any missing obligation. Long logs and symbolic expressions belong in linked evidence, not in this note. Use stable `B1` through `B5` and `Final` headings so the summary can link to them.

### PGM supplied-SOS comparison

Store the paired comparison in `details.json` and derive `supplementary/pgm-sos-comparison.md` from it. Keep `results.md` as the compact PASS/FAIL table and readable costs in `timing.md`. When `P=0`, store an empty pair list and a not-applicable reason; do not fabricate paired speedups or add an unselected condition. When `P=K`, include all `P` pair records, linked attempt IDs, eligibility, underlying outcomes, workflow completion and notebook delivery, reached blocks, actual consumed time, token totals/coverage, and execution/resource deviations for each side.

When both PGM conditions are selected, report each condition's final mathematical successes out of `K` alongside costs for all `K` slots, explicitly retaining unavailable measurements and any timeouts, incomplete or invalid runs. For pairs with comparable observed measurements, compute `without_sos - with_sos` differences in consumed generation time and complete token totals, retaining both outcomes. Missing measurements yield null differences with a reason; incomplete token totals cannot produce a complete token difference.

Report completion-time summaries separately, with their observed sample counts. Include a pair in a completed-workflow time comparison only when both attempts are eligible mathematical successes, have `run_status=completed`, and completed the workflow under the same delivery requirements; retain the matched-pair count. Otherwise leave the completion-time difference null and retain the observed consumed-cost comparison. A timeout records cutoff consumption, not workflow completion time. It may still receive mathematical PASS if its pre-cutoff submission contains a sound proof, as specified by the rubric. Do not suppress that PASS or infer unconditional speedup from successful subsets.

Include B1-B5 cost comparisons and revisit counts, with particular attention to certificate/decomposition work in B2/B3 and its downstream B4/B5 effects. Label each block-cost comparison by reachability and gate outcome; an unreached block does not count as fast completion. Compare generation and independent-review costs separately. Show input, cached-input and output usage when observed, and keep reasoning-token accounting explicit without double-counting. Missing or partial token measurements remain missing or partial in comparisons.

Use the same mathematical target and review criteria for both PGM conditions. When both conditions are selected, treat the `P` pairs as a descriptive comparison (a single paired observation when `K=1`); do not infer a general success probability or guaranteed speedup from this sample.

Optional PDF/TeX export is off by default. If requested, perform it only after generation and assessment, using [pdf-from-ipynb](../../pdf-from-ipynb/SKILL.md); save matching PDF/TeX beside each source notebook and keep supporting files supplementary. Track export costs separately and do not use export to repair frozen proofs. Report any export-discovered gap through the assessment history.

## 8. Execution and completion checks

1. Resolve missing model/evaluator settings and capabilities, preregister slots, freeze the configuration, and prepare approved fresh workspaces.
2. In each round, dispatch conditions from the preregistered round queue up to the resolved worker limit and immediately fill freed slots with the next queued condition in a fresh context and isolated workspace. Start each attempt's clock at its own dispatch; execute B1-5 sequentially within each case with measured handoffs/revisits. Stop each attempt at its own deadline and preserve its real partial work.
3. Freeze submissions at each attempt's stop. After all selected conditions in a round stop, proceed to the next round with fresh contexts. Do not inspect earlier proof content to guide later generation. Continue through round `K` without replacement runs.
4. After all `M * K` slots have terminated or been recorded as unstarted, evaluate frozen submissions under the common rubric. No post-cutoff proof repairs are accepted.
5. Finalize canonical JSON, generate the `M * K`-row and `5 * M * K`-row CSVs, the PGM paired comparison or not-applicable note, `timing.md` and the compact summary, and provide the output link.

Before reporting completion, verify exactly `M * K` unique selected condition/repetition slots, `5 * M * K` block rows and `P` PGM pairs; require exactly two PGM members per pair and preregistered order balance only when `P>0`. Check null pair IDs when unpaired, verdict mappings, relative links, hashes and count agreement across files. Reconcile measured costs without inventing missing values. Check that each displayed PASS has inspectable supporting evidence and that no invalid run is counted as an independent success. Do not claim the experiment ran merely because a plan, manifest, or empty table exists.

## 9. Preparing a paper report

Keep the operational summary compact as requested. For publication, derive a separate table from the supplementary records showing each condition's final successes out of `K`, with the two PGM conditions labeled separately, block completion results, and time/token summaries with observed sample counts. Distinguish reached-block pass rates from cumulative completion across all `K` attempts per condition. Show invalid, unreached and inconclusive cases explicitly in the paper or its appendix; the binary operational FAIL label is not a claim that every such case produced an incorrect proof.

Report the resolved repetition count and planned/observed sample counts, frozen model/settings, budgets, protocol/source/skill versions, execution mode, resolved worker limit and observed concurrency, assistance differences, isolation limitations, and reviewer procedure. Keep concurrency and resource settings comparable when comparing workflow versions; report differences that can affect timing and deadline-limited success. Separate mathematical success from notebook/workflow completion. Report all planned attempts, including timeouts; identify success-only cost summaries separately and do not equate parallel campaign elapsed time with summed attempt time. Small repetition counts, including the default five, support descriptive observations, not a broad reliability claim; a single repetition cannot establish repeatability. Archive the inputs, submitted notebooks, assessment evidence and machine-readable records alongside the paper.
