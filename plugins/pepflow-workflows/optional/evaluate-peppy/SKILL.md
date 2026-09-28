---
name: evaluate-peppy
description: "Run an explicitly requested Peppy reproducibility evaluation: selected conditions and configurable repetitions (default five for the full suite) across five paper algorithms, including PGM with and without supplied SOS, with block costs and proof assessment. Optional; do not run during ordinary analysis, skill edits, or pytest."
---

# Evaluate Peppy

Evaluate the Peppy Block 1-5 workflow on PGM, OGM, BPPM, FEG, and Dual-FEG. PGM runs with and without the fixed supplied SOS candidate; the other algorithms each have one condition. Use all six conditions by default, or the user's selected nonempty subset `C`. Each selected condition gets `K = repetitions` independent discovery attempts (normally 5): `len(C) * K` attempts in total (30 for the default full suite). An explicit request to time one named condition defaults to one repetition. Judge the final result by whether its Lyapunov proof establishes the exact target convergence guarantee; the potential and decomposition may differ from the paper.

The campaign protocol is `2026-09-20.isolation-recovery-v1`: retain the frozen branch's mathematical Block 1-5 gates, candidate-SOS assistance, and evaluation-only presentation override. Add import/configuration preflight and evidence-based operational recovery; this version applies to newly prepared campaigns, not frozen historical runs.

This is an optional controller command, separate from the five mathematical blocks and ordinary pytest/CI. Run only when the user explicitly asks for this evaluation. Creating, editing, reviewing, or mentioning the skill does not authorize launching the experiments.

## Invocation

```text
$evaluate-peppy using GPT-6 Astra with medium reasoning for generation and evaluation
```

The model above is an example, not a default. Ask for the provider/model and any applicable inference setting only when they cannot be resolved from the user's request. Reuse settings already supplied for this run. Use the same model and inference settings for evaluation unless the user specifies otherwise; verify supported settings without silently substituting a model or reasoning level.

Accept `conditions=<condition_id,...>` or an unambiguous natural-language selection, plus `repetitions=<positive integer>` or a natural-language count such as "two repetitions per condition." Default to all six conditions and five repetitions; for an explicit request to time one named condition use one repetition unless overridden. Clarify invalid or ambiguous selections/counts, including an unspecified PGM assistance variant, before dispatch. Freeze the same count for every selected condition. With `M=len(C)`, register `M*K` attempts and `5*M*K` block records; register `K` PGM pairs only when both PGM conditions are selected, otherwise none. Unselected conditions are not failed or unstarted attempts. For the full suite, `repetitions=2` gives 12 attempts, 60 block records and two pairs. Repetition count does not set concurrency.

A natural-language request to use `evaluate-peppy`, the plugin skill entry, or the Claude command can invoke this same procedure. The execution protocol does not depend on a specific AI provider or tool syntax.

Defaults are five repetitions of each of the six conditions, parallel execution with up to five available workers per round and rounds sequential, 120 minutes per attempt, no token cap, recovery through N=12, and PDF/TeX export disabled. Use the workflow's preregistered queues restricted to the selected conditions, with balanced randomized PGM pair order when both PGM conditions are selected. Queue conditions that do not fit and start the next condition as soon as a worker slot is free; finish all selected conditions before the next round. State the selected conditions, resolved repetition count, total attempts, defaults and worker limit before dispatch. Fewer than five available workers do not require additional approval under this policy. Honor explicit overrides, including an exact simultaneous-worker requirement, and confirm that fresh independent contexts are available. Do not ask the user to restate defaults or authorize every round.

Freeze the same model/reasoning, mathematical criteria, solver/resources and budgets for both PGM conditions. Prepare common validation tools and verify the actual time/token collector before dispatch; use accessible host usage logs when agent replies omit counters. Preserve fresh clean-room contexts for each condition and repetition.

Preflight the actual helper-import and static-tool configuration routes using the reviewed [static-check adapter](scripts/check_static.py). A trivial calculation or tool version check alone is insufficient. Apply the worker-safe [tool recovery policy](references/tool-recovery.md): repair ordinary path/configuration errors in the same session and original budget; a path diagnostic or limited audit visibility alone does not establish contamination. Required checks still have to pass. Confirmed prohibited exposure stops the attempt; independently assess the evidence rather than inheriting a worker's terminal label as proof.

Evaluation defaults to one independent review session per frozen submission, with the same per-submission wall-time cap as generation and no token cap. This is a configurable protocol limit, not an expected review duration. Use the submitted evidence only; unresolved validity at the review limit remains `REVIEW`. Record any human adjudication separately; none is required as an execution default.

## Read and route

For the requested campaign, read:

1. [Campaign workflow](references/workflow.md) for preparation, measurement, execution and output schemas.
2. [Clean-room policy](references/clean-room.md) for allowed inputs and access auditing.
3. [Case inputs](references/case-inputs.md) to prepare the common assumptions, one condition-specific packet per worker, and the declared aid for `pgm_with_sos` only.
4. [Worker protocol](references/worker-protocol.md) for the generation-only instructions.
5. [Evaluation operations](references/evaluation-operations.md) for actual-worker generic preflight, controller accounting/continuation helpers and the evaluation-only presentation override.
6. [Evaluation rubric](references/evaluation-rubric.md) to freeze the controller/evaluator targets and assessment policy before dispatch; perform mathematical review only after all generation stops.

Default generation performs no browser launch, screenshots or image inspection. Rendering diagnostics are ancillary, may use only an existing permitted bounded route after generation is frozen, and cannot stop dispatch, block handoffs or finalization or cause a block/delivery/final FAIL. Required notebook content, proof/source checks and clean-kernel execution remain mandatory. The worker protocol states this evaluation-only override explicitly; record it separately from the frozen mathematical skill hashes.

These references are the canonical runnable protocol. No archived proposals or paper PDFs are required to execute it. Freeze the actual framework, active mathematical skills, reference files, input packets and settings used. Do not alter the tested `pepflow/` source or active skills during a campaign.

The controller's conversation and this full skill contain evaluation information. Never use them as a generation worker's inherited context. Dispatch only fresh contexts with the worker protocol, clean-room policy, common assumptions, their own case packet/declared aid, approved generic mathematical skills and resolved operational settings. Exclude this controller workflow, `evaluation-operations.md`, controller scripts, the evaluation rubric and other cases' material from worker-readable paths. Do not copy the entire workflow plugin into a worker workspace without filtering its evaluator and solved-example resources.

## Results

Resolve `examples_peppy/_evaluations/<campaign_id>/` from the evaluated repository root, not from an installed plugin's cache directory. Keep a separate condition/repetition notebook, setup module, real `state/` artifacts and `supplementary/` evidence. Do not fabricate completed blocks or replace failed attempts.

- `results.md`: a compact table of linked Block 1-5 and final PASS/FAIL results for all `M*K` selected attempts.
- `timing.md`: readable block, generation, review and preparation costs with coverage limitations, linked to canonical measurements.
- `supplementary/runs.csv`: `M*K` attempt records with total time, token usage and underlying outcome.
- `supplementary/blocks.csv`: `5*M*K` block records, including revisits and unreached blocks.
- `supplementary/pgm-sos-comparison.md`: `K` paired PGM outcomes and time/token comparisons when both conditions are selected, otherwise an explicit not-applicable note.
- `supplementary/details.json`, `manifest.json` and brief assessment notes: actual settings, measurements, reasons and inspectable verification evidence.

Keep mathematical proof validity separate from notebook delivery and operational status. Preserve unavailable measurements, inconclusive review and contamination explicitly in the detailed records. A binary FAIL means success was not established under the protocol, not necessarily that a submitted theorem is false.

Report the campaign result location and actual completion state. Do not claim execution or successful reproduction merely because instructions or empty tables were created. The workflow includes the materials to preserve for publication: the versioned skill, the exact worker inputs, settings, submissions and assessment records.
