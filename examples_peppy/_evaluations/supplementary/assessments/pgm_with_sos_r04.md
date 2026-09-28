# pgm_with_sos_r04

The explicit submitted Lyapunov sequence satisfies exact general step, base, terminal and N=1 identities. Verified signs give V_N<=0 and hence h(x_N)-h(x_star)<=L R^2/(4N) for every N>=1 under the supplied assumptions.

Operational status: completed. Access: recovered; eligible: True. Inspected own source records, scoped host access calls and static import origins. Ordinary helper/import/static recovery and a mistyped nonexistent working directory were recorded, then checks passed from the assigned scope. No concrete prohibited-content exposure identified in inspected evidence. Instruction-only controls do not prove exhaustive access isolation. Evidence: pgm_with_sos/r04/supplementary/consulted-sources-final.json; pgm_with_sos/r04/supplementary/b4-handoff.json; supplementary/evaluation/pgm_with_sos_r04/own-generation-host-access-calls.json.

## B1

PASS: Setup implements the supplied proximal-gradient recursion, squared-radius initial condition and last-iterate composite objective; all seven prescribed sweep samples support the candidate rate.

Time: 438.033381 seconds; tokens: 1339232 (complete). Evidence: [pgm_with_sos/r04/state/pgm_b1.json](../../pgm_with_sos/r04/state/pgm_b1.json), [pgm_with_sos/r04/pgm_example_lyap.ipynb#0cf9100b](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#0cf9100b)

## B2

PASS: Final refined coherent dual certificate and the supplied SOS pass complete numerical verification. The aid normalization is one; lambda formulas are documented as candidates at discovery and proved later.

Time: 832.92336 seconds; tokens: 3548069 (complete). Evidence: [pgm_with_sos/r04/state/pgm_b2.json](../../pgm_with_sos/r04/state/pgm_b2.json), [pgm_with_sos/r04/state/pgm_selected_raw.json](../../pgm_with_sos/r04/state/pgm_selected_raw.json), [pgm_with_sos/r04/pgm_example_lyap.ipynb#592c7ed9](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#592c7ed9), [supplementary/evaluation/pgm_with_sos_r04/validation/review_replay.log](../evaluation/pgm_with_sos_r04/validation/review_replay.log)

## B3

PASS: The same forward optimizer/consecutive grouping with all three supplied squares covers the complete certificate and has constant interior rank at two horizons after refinement. No terminal leftovers are omitted.

Time: 729.3181910000001 seconds; tokens: 4013988 (complete). Evidence: [pgm_with_sos/r04/pgm_example_lyap.ipynb#b2faa91f](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#b2faa91f), [pgm_with_sos/r04/pgm_example_lyap.ipynb#8603276b](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#8603276b), [pgm_with_sos/r04/supplementary/b2-N6-certificate.json](../../pgm_with_sos/r04/supplementary/b2-N6-certificate.json), [supplementary/evaluation/pgm_with_sos_r04/validation/review_replay.log](../evaluation/pgm_with_sos_r04/validation/review_replay.log)

## B4

PASS: Independent selected bases and symmetric coefficient matrices reconstruct every partial sum k=0,...,4 including function coordinates and constants. Actual candidate scan and sparsity search are inspectable.

Time: 586.101906 seconds; tokens: 3624894 (complete). Evidence: [pgm_with_sos/r04/pgm_example_lyap.ipynb#c747d144](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#c747d144), [pgm_with_sos/r04/pgm_example_lyap.ipynb#ab155749](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#ab155749), [pgm_with_sos/r04/pgm_example_lyap.ipynb#05cc8a45](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#05cc8a45), [pgm_with_sos/r04/pgm_example_lyap.ipynb#0f27e138](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#0f27e138), [supplementary/evaluation/pgm_with_sos_r04/validation/review_replay.log](../evaluation/pgm_with_sos_r04/validation/review_replay.log)

## B5

PASS: The submitted explicit potential and supplied-square residual identities establish the exact target at arbitrary N. Every necessary multiplier and square coefficient has a direct valid sign argument. Base, terminal, N=1 and R=0 are covered.

Time: 647.236614 seconds; tokens: 2770793 (complete). Evidence: [pgm_with_sos/r04/pgm_example_lyap.ipynb#730cf5b4](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#730cf5b4), [pgm_with_sos/r04/pgm_example_lyap.ipynb#864738cf](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#864738cf), [pgm_with_sos/r04/pgm_example_lyap.ipynb#e5719f7f](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#e5719f7f), [pgm_with_sos/r04/pgm_example_lyap.ipynb#35b985d5](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#35b985d5), [pgm_with_sos/r04/pgm_example_lyap.ipynb#bc6805ed](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#bc6805ed), [pgm_with_sos/r04/supplementary/b5-final-execution.log](../../pgm_with_sos/r04/supplementary/b5-final-execution.log), [pgm_with_sos/r04/supplementary/pgm_example_lyap_checklist.md](../../pgm_with_sos/r04/supplementary/pgm_example_lyap_checklist.md), [supplementary/evaluation/pgm_with_sos_r04/validation/review_replay.log](../evaluation/pgm_with_sos_r04/validation/review_replay.log)

## Final

PASS: The explicit submitted Lyapunov sequence satisfies exact general step, base, terminal and N=1 identities. Verified signs give V_N<=0 and hence h(x_N)-h(x_star)<=L R^2/(4N) for every N>=1 under the supplied assumptions.

Matches convex L-smooth f, closed proper convex g, Euclidean finite-dimensional setting, squared-radius initial condition, final composite objective gap, general L>0 and R>=0, exact 1/(4N) constant and all N>=1. No stronger structural assumptions introduced.

Inspected frozen notebook source/output, states, generic skills, saved solver/static/execution/checklist and access records. Fresh Python -I -B replay from validation executed all code cells except the numerical plot (cell 9) and exhaustive sparse search (cell 24); those saved outputs were inspected. Replayed B2 certificates at N=4,6, B3 grouping/ranks, B4 adopted basis and full reconstruction, B5 exact arbitrary-index algebra. No new solver sweep, full Jupyter kernel execution, rendering or export during review. No proof repair.

Evidence: [pgm_with_sos/r04/pgm_example_lyap.ipynb#730cf5b4](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#730cf5b4), [pgm_with_sos/r04/pgm_example_lyap.ipynb#7cb91085](../../pgm_with_sos/r04/pgm_example_lyap.ipynb#7cb91085), [supplementary/evaluation/pgm_with_sos_r04/validation/review_replay.log](../evaluation/pgm_with_sos_r04/validation/review_replay.log)
