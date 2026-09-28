# pgm_without_sos_r03

The submitted finite-product Lyapunov certificate proves h(x_N)-h(x_star)<=L||x_0-x_star||^2/(4N)<=LR^2/(4N) for all integer N>=1. The general step, separate base/terminal and N=1 identities pass independent exact expansion; the supplied sign argument makes the potential nonincreasing.

Operational status: completed. Access: recovered; eligible: True. Own host-call records and submitted access/static records show scoped approved-source and own-artifact reads. Routine staging/path-length, lint/type and symbolic-API failures were repaired within the same attempt; a mistyped workdir failed before execution. Preflight and required source checks were rerun successfully. No concrete prohibited-answer exposure or disqualifying generic-source substitution was found in the inspected records. This is an instruction-only, nonexhaustive audit, not certification of all possible reads.

## B1

PASS: The implementation matches proximal gradient with step 1/L, squared-radius initialization and the last composite objective gap. All seven prescribed numerical samples and the rate-comparison plot are present. N=6,7 explicitly retain optimal_inaccurate status as numerical discovery evidence.

Time: 371.310289 seconds; tokens: 1206086 (complete). Evidence: [pgm_without_sos/r03/state/pgm_b1.json](../../pgm_without_sos/r03/state/pgm_b1.json), [pgm_without_sos/r03/pgm_example_lyap.ipynb#d13b250e](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#d13b250e), [pgm_without_sos/r03/pgm_example_lyap.ipynb#2c18bea7](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#2c18bea7)

## B2

PASS: Complete saved certificates at N=4 and N=6 were replayed without solving again. The identity, signs, PSD and S reconstruction pass the frozen tolerances. Initial multiplier/S formula search is documented; global analytic full-PEP proof is explicitly not claimed.

Time: 507.829347 seconds; tokens: 1847744 (complete). Evidence: [pgm_without_sos/r03/state/pgm_b2.json](../../pgm_without_sos/r03/state/pgm_b2.json), [pgm_without_sos/r03/supplementary/pgm_b2_N6.json](../../pgm_without_sos/r03/supplementary/pgm_b2_N6.json), [supplementary/evaluation/pgm_without_sos_r03/validation/numeric-replay.txt](../evaluation/pgm_without_sos_r03/validation/numeric-replay.txt), [pgm_without_sos/r03/pgm_example_lyap.ipynb#39777061](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#39777061)

## B3

PASS: The same reverse-LDL/latest-gradient assignment gives rank four on all retained interior indices at N=4 and N=6. Endpoint exclusions are fixed at one on each end. All residual families and S pieces are covered, with nonpositive residual and subtracted PSD sign conventions.

Time: 514.112819 seconds; tokens: 2259428 (complete). Evidence: [pgm_without_sos/r03/pgm_example_lyap.ipynb#3f7d5d27](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#3f7d5d27), [pgm_without_sos/r03/supplementary/rank_search.json](../../pgm_without_sos/r03/supplementary/rank_search.json), [pgm_without_sos/r03/supplementary/b3-initial-trials.json](../../pgm_without_sos/r03/supplementary/b3-initial-trials.json), [supplementary/evaluation/pgm_without_sos_r03/validation/numeric-replay.json](../evaluation/pgm_without_sos_r03/validation/numeric-replay.json)

## B4

PASS: Fresh replay of the actual candidate scan, sparse basis search, symmetric coefficient extraction and full-potential assembly passed for every required index k=0,...,4, including both endpoints.

Time: 451.132878 seconds; tokens: 2300169 (complete). Evidence: [pgm_without_sos/r03/pgm_example_lyap.ipynb#555014d6](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#555014d6), [pgm_without_sos/r03/pgm_example_lyap.ipynb#8a709058](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#8a709058), [pgm_without_sos/r03/pgm_example_lyap.ipynb#566026a9](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#566026a9), [pgm_without_sos/r03/pgm_example_lyap.ipynb#6fb2ff99](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#6fb2ff99), [pgm_without_sos/r03/pgm_example_lyap.ipynb#ccc7c313](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#ccc7c313), [supplementary/evaluation/pgm_without_sos_r03/validation/numeric-replay.json](../evaluation/pgm_without_sos_r03/validation/numeric-replay.json)

## B5

PASS: The submitted explicit finite-product potential and local SOS identities establish the exact rate for every N>=1. Independent exact expansion verifies the general step, base, terminal and N=1 identities; the submitted positive-denominator argument and residual signs imply decrease and the exact terminal normalization.

Time: 1133.504152 seconds; tokens: 4937467 (complete). Evidence: [pgm_without_sos/r03/pgm_example_lyap.ipynb#52b4381f](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#52b4381f), [pgm_without_sos/r03/pgm_example_lyap.ipynb#bb4ae8e2](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#bb4ae8e2), [pgm_without_sos/r03/pgm_example_lyap.ipynb#a895ac2f](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#a895ac2f), [pgm_without_sos/r03/pgm_example_lyap.ipynb#f50faaf0](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#f50faaf0), [pgm_without_sos/r03/pgm_example_lyap.ipynb#b600eb98](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#b600eb98), [pgm_without_sos/r03/pgm_example_lyap.ipynb#9542bab3](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#9542bab3), [pgm_without_sos/r03/pgm_example_lyap.ipynb#f8789bdd](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#f8789bdd), [supplementary/evaluation/pgm_without_sos_r03/validation/exact_audit.py](../evaluation/pgm_without_sos_r03/validation/exact_audit.py), [supplementary/evaluation/pgm_without_sos_r03/validation/exact_audit.json](../evaluation/pgm_without_sos_r03/validation/exact_audit.json), [pgm_without_sos/r03/supplementary/b5-static-001.json](../../pgm_without_sos/r03/supplementary/b5-static-001.json), [pgm_without_sos/r03/supplementary/b5-final-notebook-output.txt](../../pgm_without_sos/r03/supplementary/b5-final-notebook-output.txt)

## Final

PASS: The submitted finite-product Lyapunov certificate proves h(x_N)-h(x_star)<=L||x_0-x_star||^2/(4N)<=LR^2/(4N) for all integer N>=1. The general step, separate base/terminal and N=1 identities pass independent exact expansion; the supplied sign argument makes the potential nonincreasing.

Matches the exact target: prescribed algorithm, last-iterate composite objective gap, arbitrary finite-dimensional real Euclidean space, L>0, R>=0 and every integer N>=1. General L is retained analytically, the radius enters only through the final inequality, and no strengthened structural assumption is used.

Read only this frozen submission and its approved generic resources. Verified all 181 frozen file hashes. Fresh isolated Python -I -B replayed the submitted setup, full saved-certificate checks, both horizon groupings, actual basis search and all-index reconstruction, with runtime paths redirected into this review directory. Separately transcribed the submitted analytic formulas into an independent SymPy coefficient audit; no missing lemma or coefficient was supplied. Solver runs, full clean-kernel notebook execution and static tools were inspected from frozen logs, not rerun. No browser/rendering/export or outside mathematical source was used.

Evidence: [pgm_without_sos/r03/pgm_example_lyap.ipynb#52b4381f](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#52b4381f), [pgm_without_sos/r03/pgm_example_lyap.ipynb#bb4ae8e2](../../pgm_without_sos/r03/pgm_example_lyap.ipynb#bb4ae8e2), [supplementary/evaluation/pgm_without_sos_r03/validation/exact_audit.json](../evaluation/pgm_without_sos_r03/validation/exact_audit.json), [supplementary/evaluation/pgm_without_sos_r03/validation/numeric-replay.json](../evaluation/pgm_without_sos_r03/validation/numeric-replay.json)
