Notebook: pgm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: ae0ea255e9054f612a71ccc83604ad5717aee7ead9cbad921778c519b1146748
Presentation policy: evaluation-ancillary-v1. No browser/rendered/image review performed. Markdown delimiters, control characters and saved outputs checked under that override.
Static checks: supplementary/b5-static-001.json. Final clean-kernel nbconvert execution: supplementary/b5-final-execution.log.

| Item | Status | Cell indices | Evidence |
|---|---|---|---|
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Assumptions, proximal relation and metric present. |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1,2,3 | Placeholder replaced by separate proof heading, theorem with full potential and self-contained detailed proof outline. |
| 3. imports | verified | 4,5 | Approved-path bootstrap and imports executed. |
| 4. function/operator definitions | verified | 6 | f smooth convex, g convex, h sum; parameters defined. |
| 5. make_ctx_pgm and get_pep_setup | verified | 7 | Actual recursion, composite stationary point, squared radius constraint and objective exposed. |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 8,9,10 | All seven printed solver values and statuses retained; executed image/png comparison plot present. |
| 7. dense and relaxed proof solves | verified | 11,12 | Dense/relaxed values, all group summaries, basis and sparsity recipe replayed. Refinement to derived-lambda dual formulation documented. |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 13,14,15,47 | All dual families, labeled multiplier/SOS matrices, reconstruction and complete residual checks executed. Global formula later established by exact local identities and explicit telescoping. |
| 9. partial-sum Lyapunov construction and rank profile | verified | 16,17,18 | Visible lyap/partial_sum loop; complete certificate replay and coverage; fixed (1,1) exclusions and rank 4 at N4,N6. |
| 10. special-vector identification | verified | 19-26 | Real candidate scan and sparse-basis search output retained for every searched index; adopted basis independence checked including endpoints. |
| 11. coefficient extraction and closed-form V_k | verified | 27-34 | All numerical coefficient matrices, full function/constant terms and endpoint reconstructions; labeled exact candidate matrices and final full formula. Arbitrary-index identities establish formula. |
| 12. symbolic step, base, and boundary identities | verified | 35-49 | Separate symbolic PEPFlow contexts with actual LHS/RHS/diff; all-coordinate exact zeros for step, base, boundary and N1; denominator signs, telescope and normalization established. |