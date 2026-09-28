# Worker protocol

This complete reference is safe to send to every generation worker, together with the [clean-room rules](clean-room.md), common assumptions and its own case packet, its frozen operational settings, and approved generic workflow resources. The controller supplies the fixed PGM aid only for `condition_id=pgm_with_sos`; `pgm_without_sos` receives the same PGM assumptions and unknown rate without that aid. Do not retrieve other case or condition inputs or controller/evaluator documents.

### Objective and Allowed Work

Derive a convergence theorem through the current Peppy Blocks 1-5 for the supplied algorithm and assumptions. Infer any metric or rate marked unknown. Produce the normal evolving Jupyter notebook, setup module, and block state artifacts.

Read and follow the active skills in order within this single attempt session. Parallel execution applies across independent condition attempts; each attempt retains its sequential Block 1-5 workflow:

1. `pep-implement`: implement the algorithm, obtain numerical evidence, and initialize the notebook.
2. `pep-full-proof`: perform the full-PEP certificate analysis required by the active skill.
3. `lyap-define`: construct the Lyapunov partial sums.
4. `lyap-vectors`: find the basis and coefficient representation.
5. `lyap-closed-form`: state and verify the Lyapunov theorem and finalize the notebook.

Continue across routine block handoffs without requiring a human to type the next command. Respect the active mathematical completion gates and bounded recovery below. If a required checkpoint needs new mathematical guidance after applicable authorized recovery is exhausted, record `needs_guidance` and stop the attempt. The controller cannot act as a mathematical coauthor.

One attempt is one uninterrupted discovery session across the blocks, not one model response or one solver call. Numerical sweeps, adaptive horizon exploration, coefficient search, ordinary debugging, and corrections to your own generated files are allowed within the fixed budget. Starting a replacement session, resetting to try again from scratch, or selecting the best of multiple independent runs is prohibited.

Use the supplied fixed model, reasoning effort, budgets, and horizon limit throughout the attempt. Do not switch reasoning effort or start an adaptive reasoning ladder. Adaptive mathematical exploration below remains within those frozen settings. The controller collects all generation submissions before independent review; no reviewer corrections are available during discovery.

Only write this attempt's generated outputs. Other condition and repetition workers may be active concurrently: do not inspect their workspaces, logs, messages, or process command lines, communicate mathematical hints to them, or stop their jobs. Use only your own execution handles for process management. Do not edit the frozen framework source, installed skills, shared dependencies, supplied inputs, or evaluation rules. If a framework issue blocks the work, record it. Preserve intermediate evidence honestly; do not mark incomplete blocks complete.

### Tool Configuration and Access Recovery

Use the supplied [tool recovery policy](../../with-clean-room/references/tool-recovery.md) and reviewed static-check adapter for preflight and required source checks. Preflight must exercise local helper/framework imports and the static analyzer's actual configuration/search roots; a version check or arithmetic-only notebook is insufficient. Keep the approved adapter, pinned executable/configuration settings, and evidence destinations available through the worker allowlist.

Ordinary unresolved imports, lint/type errors, and generic repository paths in diagnostics enter operational recovery, not automatic contamination. Repair only authorized paths/configuration and your own generated files, rerun the original required checks, and continue the same attempt. No repeated user confirmation is needed for these permitted repairs. Record the original failure, repair, checks and actual source-access evidence; all elapsed time and tokens stay charged to the active block under the original deadline. Do not waive a check or edit frozen framework/skills to obtain a pass.

Stop confirmed prohibited exposure as `contaminated`. For concrete unresolved evidence of a potentially prohibited read/output, stop the suspect tool and suspend mathematical work during bounded operational triage; ordinary instruction-only visibility limitations alone do not trigger this branch. If unresolved when execution must stop, use `error` or deadline-driven `timeout`, with `access_status=unresolved`, the actual reason and partial outputs. No replacement session, silent allowlist expansion, new mathematical aid, or clock reset is permitted. The full distinctions, including blocked access and actual unapproved generic reads, are in the supplied recovery policy.

### Evaluation Presentation Policy

The controller supplies the frozen `protocol_version` and `presentation_policy=evaluation-ancillary-v1`. This is an evaluation-scoped presentation override; it does not modify the frozen mathematical skills. Keep the original B1/B2 discovery and full-certificate checks, B3 rank constancy across at least two horizons, B4 reconstruction at every required index including endpoints, and B5 exact proof obligations. Supplied PGM SOS remains candidate assistance requiring verification, not a new fixed-S solver constraint.

Do not launch a browser, capture screenshots or inspect images during generation. Retain required notebook cells and outputs, proof-critical source/static checks and clean-kernel execution. Check Markdown math delimiters and suspicious escapes inexpensively; presentation-only warnings do not block handoffs or completion. Rendering availability, image-viewer errors and missing visual-review evidence cannot fail a block, notebook delivery or the final result under this evaluation. Genuine execution failures, wrong or missing formulas and unresolved mathematical obligations retain their existing gates. Do not call a source-only check actual rendered verification or manufacture completion flags for omitted checks; record the presentation policy separately.

The controller may perform optional bounded rendering diagnostics after all generation is frozen, or arrange a separately requested visual review after assessment. Do not install, request approvals or repair tools solely for rendering, wait for those diagnostics, or use them to extend the attempt deadline. Normal mathematical checks and notebook evidence remain required.

### Adaptive Rank Recovery and Frozen Horizon Limit

Use the selected initial `N_verify`, normally 4 or 6. Within this same discovery session, diagnose indexing, signs, endpoints, and numerical rank ambiguity, then try focused interpolation-term grouping, square allocation, and alternative verified decompositions of the same `S`. If no useful observation emerges, increase `N`, normally along `4, 6, 8, 10, 12` (starting at 6 when selected), within the frozen budget. A small-horizon rank failure or three or more unsuccessful reorderings does not by itself justify `needs_guidance` while authorized recovery remains. Failed basis discovery returns to this recovery path; it never waives reconstruction.

A qualifying observation has the same numerical quadratic-matrix rank across at least two distinct horizons under a consistent construction recipe. Select fixed exclusions `a,b in {0,1,2}`, counting `V_0` and `V_N` among the exclusions; retain `a <= k <= N-b`, with at least three retained indices at each qualifying horizon. All retained ranks must agree within and across those horizons. Hold the exclusions fixed across comparisons, rechecking saved samples if the rule changes. Record rank tolerance/scaling and inspect near-threshold singular values; do not relax thresholds to manufacture agreement. Boundary exclusions affect only this comparison, not later proof obligations.

Obtain and verify each horizon's own coherent complete certificate: keep lambda, `S`, scalar/PSD extras, normalization, coordinates, setup, and verification evidence together. Verify alternative decompositions reconstruct the same `S` with required signs, and check all Gram, function-value, offset, and boundary coverage after reassignment. Carry a compatible construction recipe across samples; do not mix certificate components or merely change `N_verify` while retaining old arrays. Numerical comparison requires no analytic global lambda/`S` formula. Reuse valid samples, confirm a promising observation at another adequate authorized horizon (no greater than the frozen campaign limit), and stop escalation early when confirmed. Select one coherent horizon/certificate for the normal handoff and rebuild dependent data if selection changes. Rank agreement alone completes neither Block 3 coverage, Block 4 basis/reconstruction, nor Block 5 exact proof gates.

The campaign freezes its permitted horizon range before dispatch, normally through `N=12`. Do not solve or perform structural exploration above that frozen limit, including a confirmation-only sample. A different common range is allowed only when explicitly authorized and frozen before dispatch; do not request or accept an in-run extension. If no qualifying observation is confirmed and authorized recovery is exhausted, preserve the actual usable horizons, failed/unavailable samples, and stop reason, then stop as `stopped_at_horizon_limit`. If the original deadline arrives first, stop as `timeout`. Do not claim a horizon was successfully explored if a solver/resource failure or deadline prevented a usable certificate and rank profile. The clock continues through recovery and all model, service, tool, and resource waits. Never pause, reset, or extend the frozen budget.

Keep per-horizon certificate references, recipes, rank profiles, exclusions, tolerances, coverage results, and continuation/stop reasons in `supplementary/`, with the selected construction and concise comparison visible in the notebook. Preserve earlier samples in `supplementary/`; reserve `state/` for the selected main handoff under existing schemas. All active numerical, reconstruction, exact proof, notebook execution and required-content delivery gates remain in force, subject only to the evaluation presentation override above.

### Clean-Room Non-Leakage Clause

Read and follow the supplied [clean-room rules](clean-room.md) throughout the attempt. Use only the approved input and resources plus this attempt's own generated artifacts. The fixed PGM aid is supplied assistance only for `pgm_with_sos`; the supplied BPPM conjectured rate is the other scoped input allowance. A `pgm_without_sos` worker may discover and use its own SOS decomposition but must not read the fixed aid, its source, the other condition's answers, sibling outputs, or any other attempt's artifacts. Neither allowance permits retrieving pre-existing target solutions. A supplied aid remains a candidate to verify, never automatic certificate or proof success. Stop and report confirmed prohibited-content exposure as `contaminated`; do not restart or replace the attempt. Classify other tool/access incidents under the supplied recovery policy.

### Notebook and Block Deliverables

Use the controller-supplied `case_id`, `condition_id`, repetition, `attempt_id`, and resolved `repetitions`. The campaign freezes a selected condition list and the same positive integer `K = repetitions` for each selected condition; use the supplied resolved settings without adding conditions or repetitions. Full-suite default is `K=5`; an explicit single-condition timing request defaults to `K=1`. Both PGM conditions retain `case_id=pgm`; their condition IDs are `pgm_with_sos` and `pgm_without_sos`. For the other algorithms, `condition_id` equals `case_id`. Repetition IDs cover `1, ..., K` as `r01` onwards, with the numeric part padded to at least two digits (`r100` is valid). An attempt ID is `<condition_id>_<repetition_id>`; a PGM `pair_id` such as `pgm_r01` identifies only a matched repetition when both PGM conditions are selected; otherwise it is null.

Choose the notebook destination within the assigned `<condition_id>/<repetition_id>/` attempt directory before creating any helper files. Keep original case-based setup and notebook names, including one main notebook, `<case>_example_lyap.ipynb`, and update it through the five blocks. It must contain the algorithm, assumptions, workflow evidence, final theorem, and the proof-critical Lyapunov constructions and verification required by the active skills.

Save formal outputs to `state/<case>_b1.json` through `state/<case>_b5.json`, using the existing block schemas and retaining required solver/certificate files. Here `<case>` means `case_id`, so both PGM conditions use `state/pgm_b1.json` through `state/pgm_b5.json` inside their own attempt directory. Paths must resolve relative to that selected attempt directory or frozen source root, including when the notebook is nested inside a batch run.

Store additional scripts, logs, exploratory files, and supporting documents under the notebook's sibling `supplementary/`. Use `supplementary/.runtime/` for runtime files. Do not create separate reports duplicating the notebook or fabricate state JSON for unreached blocks.

Run the verification required by the active skills and record what was actually checked. Numerical agreement alone does not establish a theorem for arbitrary horizons. At completion or timeout, preserve the notebook and real block outputs already produced, and report completed blocks, unresolved work, consulted sources, and any access/integrity exceptions.

### Measurement handoffs and worker addendum

Execute the active Peppy Blocks 1-5 in one discovery session. Use only the
supplied input, approved generic files, and your own newly generated artifacts.
The clean-room restrictions override broad permissions to consult examples.

Maintain the main notebook and actual block states as required by the skills.
Keep supporting evidence in the notebook-adjacent supplementary/ directory.
Do not create states for unreached blocks or assert success from saved flags.

At each block handoff or revisit, report the current block, its completion
status, and the next block before starting new work. Let the controller resume
the same session automatically. This is a measurement boundary, not a request
for user permission. Keep mathematical content out of controller continuations.
Revisiting an earlier block is allowed within the original attempt budget.
Follow recovery through the frozen horizon limit. This campaign supersedes
the original protocol's request for further horizon approval: when authorized
recovery is exhausted, stop as stopped_at_horizon_limit without requesting an
extension; if the deadline arrives first, stop as timeout. Record unavailable
horizons honestly instead of claiming successful exploration of them.

Record the checks actually executed, observed residuals/tolerances, and concise
remaining obligations. Never invent time or token measurements. Do not open
aggregate results, evaluator materials, other runs, or pre-existing solutions.
Stop and report confirmed prohibited-content exposure. Classify other tool/access
incidents under the supplied recovery policy. Do not start PDF/TeX export during discovery.

Initial dispatch begins B1. Before the next request or tool operation, report a transition using operational fields such as `current_block`, `completion_status`, `next_block`, and an entry/exit reason. Align each handoff or revisit with a model request boundary: do not start substantive work on the next block within the same request. Ordinary handoff waits remain charged to the active block. Final notebook verification belongs to B5; a return from B3 to B2 for a new certificate must be labeled B2 before the solve. If a changed certificate invalidates dependent checks, revisit and recheck them.

The controller records host timestamps, elapsed intervals and provider usage. Report only observable usage and timing, and preserve `unavailable` or null when a quantity cannot be measured. A request that spans blocks without supported attribution is unallocated; do not estimate a token split. Handoffs are measurement boundaries, not human approval requests or a new independent attempt. If the runtime pauses at a handoff, await the fixed controller continuation in this same session. The original deadline continues to apply.
