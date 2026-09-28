# pgm_with_sos_r03

The submitted nonincreasing piecewise Lyapunov potential proves h(x_N)-h(x_star)<=L||x0-x_star||^2/(4N)<=LR^2/(4N) for all N>=1. Exact general interior/base/terminal/N=1 identities pass both submitted-code replay and independent polynomial expansion; coefficient signs and endpoint links complete the argument. All B1-B5 final gates pass.

Operational status: completed. Access: no_incident; eligible: True. Available own-generation host call records, preflight/import-origin records, source hashes and worker access records show no concrete prohibited-content exposure or disqualifying source read. Kernel/path-length/lint/type failures were ordinary operational errors with successful rechecks, not access incidents. The unused mistyped path string in host call 111 performed no operation. Controls were instruction-only and logs are not an exhaustive OS read audit. Fixed SOS assistance was authorized and declared. Evidence: supplementary/evaluation/pgm_with_sos_r03/own-generation-host-access-calls.json; pgm_with_sos/r03/supplementary/preflight-access-record.json; pgm_with_sos/r03/supplementary/b1-handoff.json; pgm_with_sos/r03/supplementary/b5-handoff.json.

## B1

PASS: Setup implements the supplied proximal-gradient iteration and composite terminal objective. All seven prescribed saved solves are optimal and agree with the inferred 1/(4N) rate; required notebook content and plot output are present.

Time: 454.138352 seconds; tokens: 1717329 (complete). Evidence: [pgm_with_sos/r03/state/pgm_b1.json](../../pgm_with_sos/r03/state/pgm_b1.json), [pgm_with_sos/r03/supplementary/run_b1.py](../../pgm_with_sos/r03/supplementary/run_b1.py), [pgm_with_sos/r03/pgm_example_lyap.ipynb#00c610c4](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#00c610c4), [pgm_with_sos/r03/supplementary/b1-static-003.json](../../pgm_with_sos/r03/supplementary/b1-static-003.json)

## B2

PASS: A coherent selected N=4 sparse certificate preserves the dense bound, passes all scalar-coordinate and sign/PSD checks, and reconstructs the supplied SOS at scale one. Initial multiplier-formula search is documented and checked. These are numerical certificate results, not an all-horizon global certificate claim.

Time: 770.2361960000001 seconds; tokens: 4183584 (complete). Evidence: [pgm_with_sos/r03/state/pgm_b2.json](../../pgm_with_sos/r03/state/pgm_b2.json), [pgm_with_sos/r03/state/pgm_dense.json](../../pgm_with_sos/r03/state/pgm_dense.json), [pgm_with_sos/r03/pgm_example_lyap.ipynb#03852b9e](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#03852b9e), [pgm_with_sos/r03/pgm_example_lyap.ipynb#dacc9668](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#dacc9668), [supplementary/evaluation/pgm_with_sos_r03/validation/review-replay.log](../evaluation/pgm_with_sos_r03/validation/review-replay.log)

## B3

PASS: The same forward/minimizer-pair grouping with transported SOS pieces gives rank four at N=4 and N=6, with fixed endpoint exclusions (1,1). Each horizon uses its own coherent certificate. All terms are covered, with only the initial-condition normalization reserved for the boundary argument.

Time: 742.7022039999999 seconds; tokens: 4113994 (complete). Evidence: [pgm_with_sos/r03/pgm_example_lyap.ipynb#7f4ef12e](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#7f4ef12e), [pgm_with_sos/r03/pgm_example_lyap.ipynb#ac2aa77b](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#ac2aa77b), [pgm_with_sos/r03/state/pgm_b3.json](../../pgm_with_sos/r03/state/pgm_b3.json), [pgm_with_sos/r03/supplementary/N6-selected/pgm_b2.json](../../pgm_with_sos/r03/supplementary/N6-selected/pgm_b2.json), [supplementary/evaluation/pgm_with_sos_r03/validation/review-replay.json](../evaluation/pgm_with_sos_r03/validation/review-replay.json)

## B4

PASS: Actual candidate scan and sparse basis search replayed. The selected independent basis reconstructs every required V_k at k=0,1,2,3,4, including full function-value and constant terms and both endpoint exceptions.

Time: 688.782188 seconds; tokens: 4857433 (complete). Evidence: [pgm_with_sos/r03/pgm_example_lyap.ipynb#222353c0](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#222353c0), [pgm_with_sos/r03/pgm_example_lyap.ipynb#a237245e](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#a237245e), [pgm_with_sos/r03/pgm_example_lyap.ipynb#efc34935](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#efc34935), [pgm_with_sos/r03/state/pgm_b4.json](../../pgm_with_sos/r03/state/pgm_b4.json), [pgm_with_sos/r03/supplementary/b4-reconstruction.json](../../pgm_with_sos/r03/supplementary/b4-reconstruction.json), [supplementary/evaluation/pgm_with_sos_r03/validation/review-replay.log](../evaluation/pgm_with_sos_r03/validation/review-replay.log)

## B5

PASS: The submitted piecewise potential and local interpolation/SOS identities establish the exact target for every integer N>=1. General symbolic identities were replayed and independently expanded without adding proof terms. Sign, domain, normalization and telescoping arguments are valid. Required delivery evidence is present.

Time: 925.513284 seconds; tokens: 2092699 (complete). Evidence: [pgm_with_sos/r03/pgm_example_lyap.ipynb#3bb1190b](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#3bb1190b), [pgm_with_sos/r03/pgm_example_lyap.ipynb#e7a67364](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#e7a67364), [pgm_with_sos/r03/pgm_example_lyap.ipynb#71bba802](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#71bba802), [pgm_with_sos/r03/pgm_example_lyap.ipynb#516e962f](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#516e962f), [pgm_with_sos/r03/pgm_example_lyap.ipynb#b95d2a2e](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#b95d2a2e), [pgm_with_sos/r03/pgm_example_lyap.ipynb#72f025ac](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#72f025ac), [supplementary/evaluation/pgm_with_sos_r03/validation/review-independent-symbolic.json](../evaluation/pgm_with_sos_r03/validation/review-independent-symbolic.json), [supplementary/evaluation/pgm_with_sos_r03/validation/review-replay.json](../evaluation/pgm_with_sos_r03/validation/review-replay.json), [pgm_with_sos/r03/supplementary/b5-static-002.json](../../pgm_with_sos/r03/supplementary/b5-static-002.json), [pgm_with_sos/r03/supplementary/b5-nbconvert-001.log](../../pgm_with_sos/r03/supplementary/b5-nbconvert-001.log), [pgm_with_sos/r03/supplementary/pgm_example_lyap_checklist.md](../../pgm_with_sos/r03/supplementary/pgm_example_lyap_checklist.md)

## Final

PASS: The submitted nonincreasing piecewise Lyapunov potential proves h(x_N)-h(x_star)<=L||x0-x_star||^2/(4N)<=LR^2/(4N) for all N>=1. Exact general interior/base/terminal/N=1 identities pass both submitted-code replay and independent polynomial expansion; coefficient signs and endpoint links complete the argument. All B1-B5 final gates pass.

Matches algorithm, assumptions, final-iterate composite objective, constant 1/4, general L>0 and R>=0, and every N>=1. No averaging or stronger structural assumptions; numerical normalization L=R=1 is restored exactly in the symbolic theorem.

Inspected only own frozen submission, approved generic resources and review packet. Verified all 178 frozen submission hashes. Fresh Python -I -B replay ran all 29 notebook code cells, retaining mathematical checks and omitting only cell 10 plotting; no source formula changes. Recomputed full certificate, transported SOS, rank/coverage at N=4,6, sparse basis search, every-index reconstruction, coefficient derivation and all four exact symbolic identities. Independently transcribed and expanded the same four local quadratic identities with SymPy. Solver sweeps, Ruff/ty and clean-Jupyter execution were inspected from saved source/logs/outputs, not rerun.

Evidence: [pgm_with_sos/r03/pgm_example_lyap.ipynb#a2cba0a9](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#a2cba0a9), [pgm_with_sos/r03/pgm_example_lyap.ipynb#2c88b0a5](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#2c88b0a5), [pgm_with_sos/r03/pgm_example_lyap.ipynb#72f025ac](../../pgm_with_sos/r03/pgm_example_lyap.ipynb#72f025ac), [supplementary/evaluation/pgm_with_sos_r03/validation/review-independent-symbolic.json](../evaluation/pgm_with_sos_r03/validation/review-independent-symbolic.json), [supplementary/evaluation/pgm_with_sos_r03/validation/review-replay.json](../evaluation/pgm_with_sos_r03/validation/review-replay.json), [supplementary/evaluation/pgm_with_sos_r03/validation/review-delivery-inspection.json](../evaluation/pgm_with_sos_r03/validation/review-delivery-inspection.json)
