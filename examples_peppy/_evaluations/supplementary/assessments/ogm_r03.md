# ogm_r03

The frozen submission proves f(x_N)-f(x_star) <= L R^2/(2 theta_N^2) for the exact supplied OGM at every integer N>=1. Fresh replay confirms its generic step, base, terminal, normalization and N=1 identities. The submitted sign/domain reasoning gives the correct decrease and terminal upper-bound direction.

Operational status: completed. Access: recovered; eligible: True. Inspected available own-generation access calls, preflight and handoff evidence. Observed incidents were attempt-local staging/path-length, command-argument, lint/type and symbolic-context errors, followed by successful checks. No concrete prohibited read or content exposure was found in inspected evidence. Instruction-only controls do not establish exhaustive read isolation.

## B1

PASS: The setup and visible notebook implement the supplied OGM, including the special terminal recurrence and R squared radius. All seven saved solves support the exact candidate rate; their status and comparisons were inspected and recomputed without new solves.

Time: 393.718545 seconds; tokens: 1025475 (complete). Evidence: [ogm/r03/ogm_setup.py](../../ogm/r03/ogm_setup.py), [ogm/r03/state/ogm_b1.json](../../ogm/r03/state/ogm_b1.json), [ogm/r03/ogm_example_lyap.ipynb](../../ogm/r03/ogm_example_lyap.ipynb)

## B2

PASS: Fresh reconstruction of both coherent certificates passes in Gram, function and constant coordinates; dual signs, PSD, S decomposition, inventory and source hashes pass. Dense/relaxed agreement and initial formula search are inspectable.

Time: 595.200098 seconds; tokens: 1654051 (complete). Evidence: [supplementary/evaluation/ogm_r03/validation/replay-results.json](../evaluation/ogm_r03/validation/replay-results.json), [ogm/r03/state/ogm_b2.json](../../ogm/r03/state/ogm_b2.json), [ogm/r03/supplementary/b2-N6-certificate.json](../../ogm/r03/supplementary/b2-N6-certificate.json), [ogm/r03/ogm_example_lyap.ipynb#87114f23](../../ogm/r03/ogm_example_lyap.ipynb#87114f23)

## B3

PASS: Fresh partial-sum replay covers every retained interpolation term and the complete PSD block, with terminal interpolation/S and initial radius explicitly reserved. Fixed exclusions (2,0) give rank 4 at horizons 4 and 6 with three and five retained indices.

Time: 344.586054 seconds; tokens: 1333277 (complete). Evidence: [supplementary/evaluation/ogm_r03/validation/replay-results.json](../evaluation/ogm_r03/validation/replay-results.json), [ogm/r03/ogm_example_lyap.ipynb#d081de56](../../ogm/r03/ogm_example_lyap.ipynb#d081de56), [ogm/r03/ogm_example_lyap.ipynb#437759cc](../../ogm/r03/ogm_example_lyap.ipynb#437759cc), [ogm/r03/supplementary/rank_search.json](../../ogm/r03/supplementary/rank_search.json)

## B4

PASS: Candidate scans and sparse searches were replayed. Independent adopted bases of sizes 0,3,4,4,4 reconstruct every required k=0..4, including full function and offset terms.

Time: 609.847286 seconds; tokens: 2645317 (complete). Evidence: [supplementary/evaluation/ogm_r03/validation/replay-results.json](../evaluation/ogm_r03/validation/replay-results.json), [ogm/r03/ogm_example_lyap.ipynb#bd41d035](../../ogm/r03/ogm_example_lyap.ipynb#bd41d035), [ogm/r03/ogm_example_lyap.ipynb#19cec219](../../ogm/r03/ogm_example_lyap.ipynb#19cec219), [ogm/r03/state/ogm_b4.json](../../ogm/r03/state/ogm_b4.json)

## B5

PASS: The submitted potential, exact symbolic identities and elementary domain/sign argument establish the required rate for every N>=1 and general L,R. All proof-critical code is visible; final saved clean-kernel and static evidence is complete.

Time: 825.634113 seconds; tokens: 2754160 (complete). Evidence: [ogm/r03/ogm_example_lyap.ipynb#4da4fe81](../../ogm/r03/ogm_example_lyap.ipynb#4da4fe81), [ogm/r03/ogm_example_lyap.ipynb#236274bc](../../ogm/r03/ogm_example_lyap.ipynb#236274bc), [ogm/r03/ogm_example_lyap.ipynb#4c38ad14](../../ogm/r03/ogm_example_lyap.ipynb#4c38ad14), [ogm/r03/ogm_example_lyap.ipynb#e5632836](../../ogm/r03/ogm_example_lyap.ipynb#e5632836), [supplementary/evaluation/ogm_r03/validation/replay-results.json](../evaluation/ogm_r03/validation/replay-results.json), [ogm/r03/supplementary/b5-final-nbconvert-output-002.txt](../../ogm/r03/supplementary/b5-final-nbconvert-output-002.txt)

## Final

PASS: The frozen submission proves f(x_N)-f(x_star) <= L R^2/(2 theta_N^2) for the exact supplied OGM at every integer N>=1. Fresh replay confirms its generic step, base, terminal, normalization and N=1 identities. The submitted sign/domain reasoning gives the correct decrease and terminal upper-bound direction.

Exact match of assumptions, update, output iterate, finite-horizon constant and special terminal recurrence. General parameters are retained symbolically; R=0 and N=1 are covered.

Inspected frozen source, notebook text/output, state, checklist, solver logs and access evidence. Verified every frozen submission hash. Fresh Python -I -B process replayed 25 submitted nonplot notebook code cells using only this attempt approved package root; rechecked saved certificates, partial sums, searches, reconstruction, coefficient derivation and exact identities. No fresh optimization solves, browser, rendering, export, or new Jupyter execution. Review script keeps mutable cache/temp state in validation and reads the frozen submission without modifying it.

Evidence: [ogm/r03/ogm_example_lyap.ipynb#4da4fe81](../../ogm/r03/ogm_example_lyap.ipynb#4da4fe81), [ogm/r03/ogm_example_lyap.ipynb#b533ccbf](../../ogm/r03/ogm_example_lyap.ipynb#b533ccbf), [ogm/r03/ogm_example_lyap.ipynb#e5632836](../../ogm/r03/ogm_example_lyap.ipynb#e5632836), [supplementary/evaluation/ogm_r03/validation/replay-results.json](../evaluation/ogm_r03/validation/replay-results.json)
