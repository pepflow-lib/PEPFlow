# pgm_with_sos_r05

The submitted all-horizon Lyapunov proof establishes h(x_N)-h(x_star)<=LR^2/(4N) under the supplied assumptions. Fresh replay gives exact zero step/base/terminal/N=1/normalization residuals; coefficient signs and nonincreasing direction are justified. Numerical B1-B4 evidence and final delivery also pass.

Operational status: completed. Access: recovered; eligible: True. Inspected own preflight/access and handoff records plus available host access calls. Recorded recursive helper-staging WinError 206 and later local typing/import issues were repaired within the same attempt; final source/static checks passed with own approved framework origins. No concrete prohibited exposure or unresolved access incident found in the reviewed evidence. Controls and tracing are instruction-only, not exhaustive.

## B1

PASS: Setup implements the prescribed composite proximal-gradient update, squared-radius constraint and terminal objective. All seven prescribed sweep results and rate comparison are present; inaccurate statuses are disclosed.

Time: 333.775604 seconds; tokens: 1103559 (complete). Evidence: [pgm_with_sos/r05/state/pgm_b1.json](../../pgm_with_sos/r05/state/pgm_b1.json), [pgm_with_sos/r05/pgm_example_lyap.ipynb](../../pgm_with_sos/r05/pgm_example_lyap.ipynb)

## B2

PASS: Replayed the complete selected N=4 certificate with both function families and the initial constraint; dense/sparse agreement, signs, PSD and supplied-SOS reconstruction satisfy frozen tolerances. Initial multiplier search and exact fixed-horizon verification are visible.

Time: 732.726139 seconds; tokens: 2612340 (complete). Evidence: [pgm_with_sos/r05/state/pgm_b2.json](../../pgm_with_sos/r05/state/pgm_b2.json), [pgm_with_sos/r05/state/pgm_dense.json](../../pgm_with_sos/r05/state/pgm_dense.json), [supplementary/evaluation/pgm_with_sos_r05/validation/review_replay.txt](../evaluation/pgm_with_sos_r05/validation/review_replay.txt)

## B3

PASS: The final polar-aligned decomposition reconstructs the same saved slack, has nonnegative square weights, and covers all assigned terms. The same destination-index recipe has interior rank 4 at N=4 and N=6 with one endpoint excluded at either end.

Time: 878.384831 seconds; tokens: 4145972 (complete). Evidence: [pgm_with_sos/r05/supplementary/rank_search.json](../../pgm_with_sos/r05/supplementary/rank_search.json), [pgm_with_sos/r05/pgm_example_lyap.ipynb#f1559a4e](../../pgm_with_sos/r05/pgm_example_lyap.ipynb#f1559a4e), [supplementary/evaluation/pgm_with_sos_r05/validation/review_replay.txt](../evaluation/pgm_with_sos_r05/validation/review_replay.txt)

## B4

PASS: Independent bases and symmetric coefficient matrices reconstruct the full potential at every required k=0..4, including the empty initial basis and one-vector terminal basis. Saved actual candidate scan and sparse search outputs were inspected.

Time: 526.142411 seconds; tokens: 3058819 (complete). Evidence: [pgm_with_sos/r05/state/pgm_b4.json](../../pgm_with_sos/r05/state/pgm_b4.json), [pgm_with_sos/r05/supplementary/b4-basis-probe.json](../../pgm_with_sos/r05/supplementary/b4-basis-probe.json), [supplementary/evaluation/pgm_with_sos_r05/validation/review_replay.txt](../evaluation/pgm_with_sos_r05/validation/review_replay.txt)

## B5

PASS: The submitted explicit potential, local residual identities, justified signs and endpoint normalization prove the exact target for all N>=1. Fresh symbolic replay confirms every component, including the distinct N=1 case. Saved final clean-kernel execution and static records support delivery.

Time: 1211.535627 seconds; tokens: 4100354 (complete). Evidence: [pgm_with_sos/r05/pgm_example_lyap.ipynb#efb01070](../../pgm_with_sos/r05/pgm_example_lyap.ipynb#efb01070), [pgm_with_sos/r05/pgm_example_lyap.ipynb#5e2501c9](../../pgm_with_sos/r05/pgm_example_lyap.ipynb#5e2501c9), [pgm_with_sos/r05/supplementary/b5-static-002.json](../../pgm_with_sos/r05/supplementary/b5-static-002.json), [pgm_with_sos/r05/supplementary/pgm_example_lyap_checklist.md](../../pgm_with_sos/r05/supplementary/pgm_example_lyap_checklist.md), [supplementary/evaluation/pgm_with_sos_r05/validation/review_replay.json](../evaluation/pgm_with_sos_r05/validation/review_replay.json)

## Final

PASS: The submitted all-horizon Lyapunov proof establishes h(x_N)-h(x_star)<=LR^2/(4N) under the supplied assumptions. Fresh replay gives exact zero step/base/terminal/N=1/normalization residuals; coefficient signs and nonincreasing direction are justified. Numerical B1-B4 evidence and final delivery also pass.

Exact match in assumptions, terminal (not averaged) metric, finite-horizon constant 1/(4N), L and squared-radius normalization, and all N>=1. No g(x_0) evaluation is needed. N=1 is separately proved; N=2 has only base and terminal steps.

Read frozen notebook proof and code, setup, sweep, numerical certificate/state, rank/basis/search records, generic skills, static/clean-kernel evidence and access records. Fresh Python -I -B replay from validation using only own copied approved framework: selected B2 cells; B3 certificate/decomposition/grouping at N4/N6; B4 independence and full reconstruction; B5 coefficient derivation and generic exact identities/signs. The sole execution adaptation permits original read-only source-hash provenance checks; formulas were unchanged. No solver reruns, browser, rendering or exports. Original submission hashes checked against manifest with no mismatches.

Evidence: [pgm_with_sos/r05/pgm_example_lyap.ipynb#5e2501c9](../../pgm_with_sos/r05/pgm_example_lyap.ipynb#5e2501c9), [pgm_with_sos/r05/pgm_example_lyap.ipynb#621457cc](../../pgm_with_sos/r05/pgm_example_lyap.ipynb#621457cc), [supplementary/evaluation/pgm_with_sos_r05/validation/review_replay.json](../evaluation/pgm_with_sos_r05/validation/review_replay.json), [supplementary/evaluation/pgm_with_sos_r05/validation/review_replay.txt](../evaluation/pgm_with_sos_r05/validation/review_replay.txt), [pgm_with_sos/r05/supplementary/b5-final-execution.json](../../pgm_with_sos/r05/supplementary/b5-final-execution.json)
