# feg_r04

The submitted potential has the correct nonincreasing direction, exact generic step/base/terminal identities and elementary sign/domain justifications. Its terminal identity proves ||A(x_N)||^2 <= 4 L^2 R^2/N^2 for all N>=1, including N=1 and R=0. Fresh replay validates its algebra and B2-B4 numerical checks.

Operational status: completed. Access: no_incident; eligible: True. Inspected own preflight/access records, final handoff, and available scoped host access-call evidence. No concrete prohibited exposure or unresolved source-boundary incident identified. Recorded typing, indexing and notebook-check repairs concern own artifacts. Instruction-only controls and incomplete filesystem observability do not establish contamination.

## B1

PASS: Setup implements the supplied FEG recurrence with one shared initial half-step, squared-radius initialization and final squared operator residual. All seven saved solves are optimal; the candidate is correctly labeled numerical evidence.

Time: 454.920021 seconds; tokens: 1536835 (complete). Evidence: [feg/r04/feg_setup.py](../../feg/r04/feg_setup.py), [feg/r04/state/feg_b1.json](../../feg/r04/state/feg_b1.json), [feg/r04/feg_example_lyap.ipynb#10cc4d03](../../feg/r04/feg_example_lyap.ipynb#10cc4d03)

## B2

PASS: The coherent selected N6 certificate reconstructs all constraints, Gram/function/constant components and S within frozen tolerances. The initial formula search is explicit and distinguishes its numerical mismatch from proof status.

Time: 633.355582 seconds; tokens: 2620477 (complete). Evidence: [supplementary/evaluation/feg_r04/validation/replay-results.json](../evaluation/feg_r04/validation/replay-results.json), [feg/r04/feg_example_lyap.ipynb#a9d3f288](../../feg/r04/feg_example_lyap.ipynb#a9d3f288), [feg/r04/state/feg_b2.json](../../feg/r04/state/feg_b2.json)

## B3

PASS: The same nonincreasing partial-sum recipe, with whole S and final zero-point monotonicity kept at the boundary, passes full-coordinate coverage and increment checks at N4 and N6. Fixed exclusions remove only V0 and VN.

Time: 539.7204839999999 seconds; tokens: 2785553 (complete). Evidence: [supplementary/evaluation/feg_r04/validation/replay-results.json](../evaluation/feg_r04/validation/replay-results.json), [feg/r04/feg_example_lyap.ipynb#9788f06b](../../feg/r04/feg_example_lyap.ipynb#9788f06b), [feg/r04/supplementary/b3-rank-confirmed-N4.json](../../feg/r04/supplementary/b3-rank-confirmed-N4.json), [feg/r04/supplementary/b3-rank-confirmed-N6.json](../../feg/r04/supplementary/b3-rank-confirmed-N6.json)

## B4

PASS: The actual 348-vector scan and sparse searches are retained and replayed. The common basis [A(x_k),x_k-x_0] is independent and reconstructs every required Vk, including empty V0 and terminal V6.

Time: 343.649907 seconds; tokens: 2361981 (complete). Evidence: [supplementary/evaluation/feg_r04/validation/replay-results.json](../evaluation/feg_r04/validation/replay-results.json), [feg/r04/feg_example_lyap.ipynb#ce0ae73b](../../feg/r04/feg_example_lyap.ipynb#ce0ae73b), [feg/r04/feg_example_lyap.ipynb#5537f246](../../feg/r04/feg_example_lyap.ipynb#5537f246), [feg/r04/supplementary/b4-search-evidence.json](../../feg/r04/supplementary/b4-search-evidence.json)

## B5

PASS: The complete submitted arbitrary-horizon Lyapunov argument establishes exactly 4 L^2 R^2/N^2. Exact symbolic replay confirms step, base and terminal identities, and the displayed elementary signs imply decrease and the claimed bound.

Time: 485.200772 seconds; tokens: 2679340 (complete). Evidence: [supplementary/evaluation/feg_r04/validation/replay-results.json](../evaluation/feg_r04/validation/replay-results.json), [feg/r04/feg_example_lyap.ipynb#10b9b0a5](../../feg/r04/feg_example_lyap.ipynb#10b9b0a5), [feg/r04/feg_example_lyap.ipynb#f0bee20b](../../feg/r04/feg_example_lyap.ipynb#f0bee20b), [feg/r04/feg_example_lyap.ipynb#dc01176f](../../feg/r04/feg_example_lyap.ipynb#dc01176f), [feg/r04/feg_example_lyap.ipynb#5dd131dc](../../feg/r04/feg_example_lyap.ipynb#5dd131dc), [feg/r04/supplementary/b5-static-002.json](../../feg/r04/supplementary/b5-static-002.json), [feg/r04/supplementary/b5-final-execution.json](../../feg/r04/supplementary/b5-final-execution.json), [feg/r04/supplementary/feg_example_lyap_checklist.md](../../feg/r04/supplementary/feg_example_lyap_checklist.md), [supplementary/evaluation/feg_r04/validation/inspection-results.json](../evaluation/feg_r04/validation/inspection-results.json)

## Final

PASS: The submitted potential has the correct nonincreasing direction, exact generic step/base/terminal identities and elementary sign/domain justifications. Its terminal identity proves ||A(x_N)||^2 <= 4 L^2 R^2/N^2 for all N>=1, including N=1 and R=0. Fresh replay validates its algebra and B2-B4 numerical checks.

Exact match of algorithm, assumptions, final-iterate squared residual metric, constant 4, L^2 R^2 normalization and all horizons N>=1. No strengthened assumptions or averaged iterate.

Inspected frozen notebook/source, saved sweep, coherent numerical certificate and discovery artifacts, submitted proof, saved static/clean-kernel logs and checklist. Replayed 26 notebook code cells in a fresh pinned Python -I -B process in validation, omitting the plotting cell; independently replayed N4 certificate/decomposition/grouping from its own saved certificate. Exact general step/base/terminal checks use symbolic k,N,L,R rather than finite horizon substitutions. Verified all frozen hashes. No new solves, proof repair, outside mathematical sources, rendering or exports.

Evidence: [feg/r04/feg_example_lyap.ipynb#10b9b0a5](../../feg/r04/feg_example_lyap.ipynb#10b9b0a5), [feg/r04/feg_example_lyap.ipynb#5473c371](../../feg/r04/feg_example_lyap.ipynb#5473c371), [supplementary/evaluation/feg_r04/validation/replay-results.json](../evaluation/feg_r04/validation/replay-results.json), [supplementary/evaluation/feg_r04/validation/inspection-results.json](../evaluation/feg_r04/validation/inspection-results.json)
