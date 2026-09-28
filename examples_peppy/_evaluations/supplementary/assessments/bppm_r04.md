# bppm_r04

The explicit potential V_k=(D_h(x_star,x_k)-D_h(x_star,x_0))/(alpha*N)+(k/N)(f(x_k)-f(x_star)) has the submitted exact nonpositive-residual increment. With V_0=0 and the exact terminal identity it proves f(x_N)-f(x_star)<=R/(alpha*N) for every integer N>=1, alpha>0 and R>=0 under the supplied assumptions. All seven exact symbolic identities and numerical B2-B4 checks replayed successfully.

Operational status: completed. Access: recovered; eligible: True. Available own-host tool calls, consulted-source records and static/preflight reports show attempt-owned files, approved generic sources and pinned dependencies. Recorded path-length staging, import/type diagnostics and audit-parser errors were repaired in the same attempt; no concrete prohibited exposure was identified. Final static checks passed. Instruction-only isolation and nonexhaustive source tracing limit this conclusion; they are not evidence of contamination.

## B1

PASS: Setup implements exact Bregman proximal updates, initial divergence <= R, and last-iterate objective gap. All seven required saved sweep solves are optimal and support the supplied candidate rate; notebook contains the setup and saved numerical evidence.

Time: 422.702908 seconds; tokens: 1320880 (complete). Evidence: [bppm/r04/bppm_setup.py](../../bppm/r04/bppm_setup.py), [bppm/r04/supplementary/b1_sweep-002.console.txt](../../bppm/r04/supplementary/b1_sweep-002.console.txt), [bppm/r04/bppm_example_lyap.ipynb](../../bppm/r04/bppm_example_lyap.ipynb)

## B2

PASS: Replayed the complete saved N=4 and N=6 certificates with their own coordinate inventories, source hashes, multipliers and S. Full scalar identities, dual signs, PSD, eigendecomposition reconstruction and dense/relaxed agreement pass. Initial formula search is documented; global analytic lambda/S verification is explicitly not claimed.

Time: 623.7156110000001 seconds; tokens: 1984106 (complete). Evidence: [bppm/r04/bppm_example_lyap.ipynb#c039912f](../../bppm/r04/bppm_example_lyap.ipynb#c039912f), [bppm/r04/bppm_example_lyap.ipynb#ee1fb963](../../bppm/r04/bppm_example_lyap.ipynb#ee1fb963), [supplementary/evaluation/bppm_r04/validation/replay.log](../evaluation/bppm_r04/validation/replay.log), [bppm/r04/state/bppm_dense.json](../../bppm/r04/state/bppm_dense.json)

## B3

PASS: The submitted grouping assigns every active interpolation term and the entire numerical S, with one terminal h residual and one terminal PSD block. Full-coordinate coverage and increments replay successfully. A single fixed recipe has rank 4 at N=4 and N=6 with fixed one-index exclusions at each end, leaving three and five interior indices.

Time: 389.410462 seconds; tokens: 1588839 (complete). Evidence: [bppm/r04/bppm_example_lyap.ipynb#552381d0](../../bppm/r04/bppm_example_lyap.ipynb#552381d0), [bppm/r04/bppm_example_lyap.ipynb#bfb3f708](../../bppm/r04/bppm_example_lyap.ipynb#bfb3f708), [supplementary/evaluation/bppm_r04/validation/replay_summary.json](../evaluation/bppm_r04/validation/replay_summary.json)

## B4

PASS: Replayed candidate filtering, the actual sparsity search, independence tests and symmetric coefficient extraction for all nonzero indices. The assembled quadratic, function and constant expression reconstructs V_k for every k=0..4, including both endpoints.

Time: 322.115945 seconds; tokens: 1332489 (complete). Evidence: [bppm/r04/bppm_example_lyap.ipynb#07ce1939](../../bppm/r04/bppm_example_lyap.ipynb#07ce1939), [bppm/r04/bppm_example_lyap.ipynb#f3a7f8e0](../../bppm/r04/bppm_example_lyap.ipynb#f3a7f8e0), [supplementary/evaluation/bppm_r04/validation/replay.log](../evaluation/bppm_r04/validation/replay.log)

## B5

PASS: The submitted all-horizon proof establishes the exact target. Its generic step, coefficient structure, initial, first-step and terminal identities replay exactly in all scalar components. Convex residuals are nonpositive and every coefficient is nonnegative; V0=0 gives VN<=0, and the terminal identity gives metric<=R/(alpha N). N=1 and R=0 are covered. Required saved static and clean-kernel execution evidence is present.

Time: 473.074206 seconds; tokens: 2284493 (complete). Evidence: [bppm/r04/bppm_example_lyap.ipynb#04fed141](../../bppm/r04/bppm_example_lyap.ipynb#04fed141), [bppm/r04/bppm_example_lyap.ipynb#36310e94](../../bppm/r04/bppm_example_lyap.ipynb#36310e94), [bppm/r04/bppm_example_lyap.ipynb#b7276a21](../../bppm/r04/bppm_example_lyap.ipynb#b7276a21), [bppm/r04/bppm_example_lyap.ipynb#a8b4a071](../../bppm/r04/bppm_example_lyap.ipynb#a8b4a071), [bppm/r04/supplementary/b5_nbconvert.console.txt](../../bppm/r04/supplementary/b5_nbconvert.console.txt), [bppm/r04/supplementary/bppm_example_lyap_checklist.md](../../bppm/r04/supplementary/bppm_example_lyap_checklist.md), [supplementary/evaluation/bppm_r04/validation/replay_summary.json](../evaluation/bppm_r04/validation/replay_summary.json)

## Final

PASS: The explicit potential V_k=(D_h(x_star,x_k)-D_h(x_star,x_0))/(alpha*N)+(k/N)(f(x_k)-f(x_star)) has the submitted exact nonpositive-residual increment. With V_0=0 and the exact terminal identity it proves f(x_N)-f(x_star)<=R/(alpha*N) for every integer N>=1, alpha>0 and R>=0 under the supplied assumptions. All seven exact symbolic identities and numerical B2-B4 checks replayed successfully.

Matches the last-iterate objective gap, supplied algorithm and assumptions, exact finite-horizon coefficient 1/(alpha*N), radius R rather than R^2, arbitrary positive alpha, nonnegative R and all N>=1. No stronger structural assumption is introduced.

Inspected notebook source and saved outputs, setup, state, sweep/solver/static/execution logs, source records and own-host access calls. Verified all 162 frozen-file hashes in a validation copy. Freshly replayed all 24 code cells in a pinned Python -I -B process using only copied approved package/helper roots; omitted only plotting. Recomputed numerical certificate checks, rank profiles, sparse-basis reconstruction and seven exact symbolic identities. No solver re-solves, browser, rendering, exports or proof repairs. Saved static and original clean-Jupyter-kernel outcomes were inspected, not independently rerun.

Evidence: [bppm/r04/bppm_example_lyap.ipynb#83198826](../../bppm/r04/bppm_example_lyap.ipynb#83198826), [bppm/r04/bppm_example_lyap.ipynb#36310e94](../../bppm/r04/bppm_example_lyap.ipynb#36310e94), [bppm/r04/bppm_example_lyap.ipynb#b7276a21](../../bppm/r04/bppm_example_lyap.ipynb#b7276a21), [bppm/r04/bppm_example_lyap.ipynb#a8b4a071](../../bppm/r04/bppm_example_lyap.ipynb#a8b4a071), [supplementary/evaluation/bppm_r04/validation/replay_summary.json](../evaluation/bppm_r04/validation/replay_summary.json), [supplementary/evaluation/bppm_r04/own-generation-host-access-calls.json](../evaluation/bppm_r04/own-generation-host-access-calls.json), [bppm/r04/supplementary/b1-consulted-sources.json](../../bppm/r04/supplementary/b1-consulted-sources.json), [bppm/r04/supplementary/b5-consulted-sources.json](../../bppm/r04/supplementary/b5-consulted-sources.json)
