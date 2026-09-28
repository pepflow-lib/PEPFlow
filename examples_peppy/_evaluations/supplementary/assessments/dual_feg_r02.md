# dual_feg_r02

The explicit horizon-dependent potential has exact valid step, base, final-step and N=1 identities. Positive coefficients times nonpositive Lipschitz/monotonicity residuals yield VN<=0; the submitted boundary square-completion and radius condition imply ||A(xN)||^2<=4L^2R^2/N^2 for every integer N>=1.

Operational status: completed. Access: recovered; eligible: True. Inspected own generation access-call records, preflight/static resolution records, and handoff/closure incident logs. Observed reads are own artifacts and approved generic resources; no concrete prohibited exposure found. B1 staging/helper-layout and generated-source diagnostics were repaired in the same session with repeat preflight/static checks. Later type/display repairs passed final checks. These routine repairs do not invalidate eligibility. Instruction-only controls do not certify exhaustive OS reads. A disclosed BLAS environment-order issue has unknown historical thread counts and does not supply mathematical assistance.

## B1

PASS: The visible setup implements all three supplied recurrences, z0=0, zero-point and radius assumptions, and terminal squared operator residual. The saved N=1..7 sweep supports the inferred uniform rate; N=1 numerical inaccuracy is disclosed and is not used as an analytic proof.

Time: 455.132413 seconds; tokens: 1633316 (complete). Evidence: [dual_feg/r02/dual_feg_example_lyap.ipynb](../../dual_feg/r02/dual_feg_example_lyap.ipynb), [dual_feg/r02/state/dual_feg_b1.json](../../dual_feg/r02/state/dual_feg_b1.json), [dual_feg/r02/dual_feg_setup.py](../../dual_feg/r02/dual_feg_setup.py)

## B2

PASS: A coherent structural relaxation at N=6 is fully numerically certified and agrees with the dense solve. Fresh replay validates saved multipliers, all scalar coordinates, signs, PSD and numerical S decomposition. The initial closed-form search is documented; arbitrary-horizon global lambda/S proof is separately unclaimed.

Time: 563.410014 seconds; tokens: 2111221 (complete). Evidence: [dual_feg/r02/state/dual_feg_b2.json](../../dual_feg/r02/state/dual_feg_b2.json), [dual_feg/r02/state/dual_feg_dense.json](../../dual_feg/r02/state/dual_feg_dense.json), [dual_feg/r02/dual_feg_example_lyap.ipynb#7c7681fb](../../dual_feg/r02/dual_feg_example_lyap.ipynb#7c7681fb), [supplementary/evaluation/dual_feg_r02/validation/replay-results.json](../evaluation/dual_feg_r02/validation/replay-results.json)

## B3

PASS: Freshly replayed certificate and grouping checks at N=4 and N=6 give rank four at every retained interior index under the same forward-step recipe. Only terminal monotonicity and the whole PSD S remain as boundary contributions; normalization is reserved for the boundary.

Time: 423.161941 seconds; tokens: 1879361 (complete). Evidence: [dual_feg/r02/dual_feg_example_lyap.ipynb#beb981ea](../../dual_feg/r02/dual_feg_example_lyap.ipynb#beb981ea), [dual_feg/r02/supplementary/b3-rank-N4.json](../../dual_feg/r02/supplementary/b3-rank-N4.json), [dual_feg/r02/supplementary/b3-rank-N6.json](../../dual_feg/r02/supplementary/b3-rank-N6.json), [supplementary/evaluation/dual_feg_r02/validation/replay-results.json](../evaluation/dual_feg_r02/validation/replay-results.json)

## B4

PASS: Fresh replay performs actual candidate filtering and sparse-basis search, verifies the adopted basis independence and spans, and reconstructs every V_k at N=6 including both endpoints. Function and offset terms are explicitly checked as zero.

Time: 364.808024 seconds; tokens: 1787478 (complete). Evidence: [dual_feg/r02/dual_feg_example_lyap.ipynb#edfd5b58](../../dual_feg/r02/dual_feg_example_lyap.ipynb#edfd5b58), [dual_feg/r02/dual_feg_example_lyap.ipynb#a606e742](../../dual_feg/r02/dual_feg_example_lyap.ipynb#a606e742), [dual_feg/r02/dual_feg_example_lyap.ipynb#3a36351e](../../dual_feg/r02/dual_feg_example_lyap.ipynb#3a36351e), [supplementary/evaluation/dual_feg_r02/validation/replay-results.json](../evaluation/dual_feg_r02/validation/replay-results.json)

## B5

PASS: The submitted potential and identities establish the exact target for all integer N>=1. Generic-index algebra, parameter scaling, base, last step, N=1 and final square-completion are verified; the signs imply VN<=V0=0 and the claimed bound. Saved static and clean-kernel evidence is corroborated by the final executed notebook and a fresh mathematical-cell replay.

Time: 650.08499 seconds; tokens: 2690807 (complete). Evidence: [dual_feg/r02/dual_feg_example_lyap.ipynb#8bc65544](../../dual_feg/r02/dual_feg_example_lyap.ipynb#8bc65544), [dual_feg/r02/dual_feg_example_lyap.ipynb#19b11c59](../../dual_feg/r02/dual_feg_example_lyap.ipynb#19b11c59), [supplementary/evaluation/dual_feg_r02/validation/independent-exact.json](../evaluation/dual_feg_r02/validation/independent-exact.json), [supplementary/evaluation/dual_feg_r02/validation/replay-results.json](../evaluation/dual_feg_r02/validation/replay-results.json), [supplementary/evaluation/dual_feg_r02/validation/integrity-delivery.json](../evaluation/dual_feg_r02/validation/integrity-delivery.json), [dual_feg/r02/supplementary/b5-static-003.json](../../dual_feg/r02/supplementary/b5-static-003.json), [dual_feg/r02/supplementary/b5-final-nbconvert-output-002.txt](../../dual_feg/r02/supplementary/b5-final-nbconvert-output-002.txt), [dual_feg/r02/supplementary/dual_feg_example_lyap_checklist.md](../../dual_feg/r02/supplementary/dual_feg_example_lyap_checklist.md)

## Final

PASS: The explicit horizon-dependent potential has exact valid step, base, final-step and N=1 identities. Positive coefficients times nonpositive Lipschitz/monotonicity residuals yield VN<=0; the submitted boundary square-completion and radius condition imply ||A(xN)||^2<=4L^2R^2/N^2 for every integer N>=1.

Exactly matches algorithm, assumptions, terminal squared residual, finite-horizon constant 4, and general L,R. Independent symbolic verification retains generic L,N; separate N=1 proof covers the exceptional endpoint and R=0 is allowed without division. Terminal-iterate-dependent potential is permitted by rubric.

Inspected frozen notebook source and saved execution/static evidence, submitted skills/rules, numerical state/certificates and own access records. Fresh Python -I -B replay in validation rechecked 25 computational cells with original runtime import/bootstrap and all plotting/matrix display calls omitted, keeping reads on the own approved framework/state and writes/caches in validation. Replayed N=4 certificate/grouping separately. Independently expanded the submitted identities in SymPy without PEPFlow. Original solves and full Jupyter/static runs were inspected, not rerun; no browser/render/export. Frozen artifact hashes freshly checked.

Evidence: [dual_feg/r02/dual_feg_example_lyap.ipynb#19b11c59](../../dual_feg/r02/dual_feg_example_lyap.ipynb#19b11c59), [supplementary/evaluation/dual_feg_r02/validation/independent-exact.json](../evaluation/dual_feg_r02/validation/independent-exact.json), [supplementary/evaluation/dual_feg_r02/validation/replay-results.json](../evaluation/dual_feg_r02/validation/replay-results.json)
