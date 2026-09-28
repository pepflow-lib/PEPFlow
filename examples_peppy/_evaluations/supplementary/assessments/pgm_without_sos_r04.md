# pgm_without_sos_r04

The submitted horizon-dependent Lyapunov proof establishes h(x_N)-h(x_star)<=L*R^2/(4N) for every integer N>=1 under the required assumptions. Explicit finite-product coefficients, all-coordinate exact identities, justified positive quadratic blocks and interpolation multipliers, separate N=1 identity, and terminal normalization are supplied and verified.

Operational status: completed. Access: no_incident; eligible: True. No concrete prohibited exposure or unapproved source read found in inspected source records and 112 available host access calls. Textual absolute-path scan found no root outside this attempt and the pinned interpreter environment. Ordinary path-length/lint issues were repaired in-session and final checks passed; they do not establish a source-boundary incident. Instruction-only controls do not provide exhaustive filesystem observability.

## B1

PASS: Setup implements the required proximal-gradient update, sum stationarity, squared-radius constraint and last-iterate composite gap. All seven prescribed sweep results and the comparison plot are present.

Time: 439.591025 seconds; tokens: 1584916 (complete). Evidence: [pgm_without_sos/r04/state/pgm_b1.json](../../pgm_without_sos/r04/state/pgm_b1.json), [pgm_without_sos/r04/pgm_example_lyap.ipynb#f7ebb014](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#f7ebb014), [pgm_without_sos/r04/pgm_example_lyap.ipynb#a16fc29b](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#a16fc29b)

## B2

PASS: The selected complete N=4 certificate, its source/coordinate inventory and decomposition replay successfully. Dense/relaxed bounds agree, and the initial formula search is visible. Global analytic full-PEP positivity is correctly left unclaimed.

Time: 636.972895 seconds; tokens: 2900473 (complete). Evidence: [pgm_without_sos/r04/state/pgm_b2.json](../../pgm_without_sos/r04/state/pgm_b2.json), [pgm_without_sos/r04/pgm_example_lyap.ipynb#e7b477d3](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#e7b477d3), [supplementary/evaluation/pgm_without_sos_r04/validation/replay_results.json](../evaluation/pgm_without_sos_r04/validation/replay_results.json)

## B3

PASS: The same reverse-LDL/latest-iterate grouping reconstructs all terms and increments at N=4 and N=6. Each confirming horizon has at least three retained rank-four indices with fixed one-index exclusions at both ends.

Time: 544.424285 seconds; tokens: 2978709 (complete). Evidence: [pgm_without_sos/r04/pgm_example_lyap.ipynb#3b471409](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#3b471409), [pgm_without_sos/r04/pgm_example_lyap.ipynb#d4d8e853](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#d4d8e853), [pgm_without_sos/r04/supplementary/rank_search.json](../../pgm_without_sos/r04/supplementary/rank_search.json), [supplementary/evaluation/pgm_without_sos_r04/validation/replay_results.json](../evaluation/pgm_without_sos_r04/validation/replay_results.json)

## B4

PASS: The adopted independent basis and symmetric matrices reconstruct the quadratic and full scalar potential at every required index k=0..4. Actual candidate filtering and sparsity search are present and replayed.

Time: 506.147542 seconds; tokens: 2996184 (complete). Evidence: [pgm_without_sos/r04/pgm_example_lyap.ipynb#f2b7c5e8](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#f2b7c5e8), [pgm_without_sos/r04/pgm_example_lyap.ipynb#24883291](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#24883291), [pgm_without_sos/r04/pgm_example_lyap.ipynb#a0adaf5c](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#a0adaf5c), [pgm_without_sos/r04/pgm_example_lyap.ipynb#b2700e8f](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#b2700e8f), [supplementary/evaluation/pgm_without_sos_r04/validation/replay_results.json](../evaluation/pgm_without_sos_r04/validation/replay_results.json)

## B5

PASS: The finite transfer product defines every beta coefficient and satisfies the submitted recurrence. Exact symbolic replay verifies every local identity; the supplied sign/domain proof yields V_N<=V_0=0 and the exact target for all N>=1, including N=1 and N=2.

Time: 1135.360972 seconds; tokens: 6331205 (complete). Evidence: [pgm_without_sos/r04/pgm_example_lyap.ipynb#94b7f70f](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#94b7f70f), [pgm_without_sos/r04/pgm_example_lyap.ipynb#b29d06bd](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#b29d06bd), [pgm_without_sos/r04/pgm_example_lyap.ipynb#41c81074](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#41c81074), [pgm_without_sos/r04/pgm_example_lyap.ipynb#f93defbc](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#f93defbc), [pgm_without_sos/r04/pgm_example_lyap.ipynb#4a6f6f3f](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#4a6f6f3f), [pgm_without_sos/r04/supplementary/b5-final-execution.json](../../pgm_without_sos/r04/supplementary/b5-final-execution.json), [pgm_without_sos/r04/supplementary/b5-static-002.json](../../pgm_without_sos/r04/supplementary/b5-static-002.json), [pgm_without_sos/r04/supplementary/pgm_example_lyap_checklist.md](../../pgm_without_sos/r04/supplementary/pgm_example_lyap_checklist.md), [supplementary/evaluation/pgm_without_sos_r04/validation/replay_results.json](../evaluation/pgm_without_sos_r04/validation/replay_results.json)

## Final

PASS: The submitted horizon-dependent Lyapunov proof establishes h(x_N)-h(x_star)<=L*R^2/(4N) for every integer N>=1 under the required assumptions. Explicit finite-product coefficients, all-coordinate exact identities, justified positive quadratic blocks and interpolation multipliers, separate N=1 identity, and terminal normalization are supplied and verified.

Exact match: same composite last-iterate metric, update step 1/L, assumptions, squared-radius normalization and constant 1/(4N). General L is retained in the analytic checks. First/last steps, N=1, empty-product N=2, and R=0 are covered.

Inspected the frozen notebook, submitted proof/scripts, numerical state, skill requirements, source and access records. Freshly replayed all 28 code-cell mathematical contents from the validation copy in pinned Python -I -B, omitting only plotting commands; no new solves. Replayed N=6 certificate and grouping separately. Exact symbolic checks and N=4/N=6 numerical certificate/grouping and N=4 basis/reconstruction checks passed. Independently matched all 158 frozen artifact hashes. Saved solver sweep, original clean-kernel execution and final static reports were inspected, not rerun. Sign/domain and telescoping arguments were assessed from the supplied formulas, not trusted booleans.

Evidence: [pgm_without_sos/r04/supplementary/b5_theorem.md](../../pgm_without_sos/r04/supplementary/b5_theorem.md), [pgm_without_sos/r04/supplementary/b5_proof_outline.md](../../pgm_without_sos/r04/supplementary/b5_proof_outline.md), [pgm_without_sos/r04/pgm_example_lyap.ipynb#4a6f6f3f](../../pgm_without_sos/r04/pgm_example_lyap.ipynb#4a6f6f3f), [supplementary/evaluation/pgm_without_sos_r04/validation/replay_results.json](../evaluation/pgm_without_sos_r04/validation/replay_results.json), [supplementary/evaluation/pgm_without_sos_r04/validation/replay_output.txt](../evaluation/pgm_without_sos_r04/validation/replay_output.txt), [supplementary/evaluation/pgm_without_sos_r04/validation/audit_results.json](../evaluation/pgm_without_sos_r04/validation/audit_results.json), [supplementary/evaluation/pgm_without_sos_r04/own-generation-host-access-calls.json](../evaluation/pgm_without_sos_r04/own-generation-host-access-calls.json)
