Notebook: bppm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: f2052f149ad8608bfdfb10b13c0b5454f027616a398890807ef3be1ec0a2dff5
Presentation policy: evaluation-ancillary-v1. Source and executed outputs inspected; no rendering, browser or image inspection performed or claimed.

| Item | Status | Cell indices | Evidence |
|---|---|---|---|
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Assumptions, exact updates, Bregman definition, radius R and metric stated. |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1–3 | Separate proof heading, theorem with full potential, and self-contained residual identities/telescoping. |
| 3. imports | verified | 4–6,29,40 | Approved framework and installed dependencies; all import cells executed. |
| 4. function/operator definitions | verified | 7 | Convex f and h definitions visible and executed. |
| 5. make_ctx_bppm and get_pep_setup | verified | 8 | Visible context builder, proximal update, initialization and metric executed. |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 9–11 | Seven printed CLARABEL optima, discrepancy 3.62e-9, and stored matplotlib comparison output. |
| 7. dense and relaxed proof solves | verified | 12–13 | Dense/sparse solve provenance, both owners multiplier matrices and bound preservation displayed. |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 14–19 | Initial candidate search, selected S spectral decomposition, true S and residual matrices, signs and complete scalar identity rechecked; global analytic status explicitly separate. |
| 9. partial-sum Lyapunov construction and rank profile | verified | 20–25 | Visible partial-sum loop, full component coverage, terminal leftovers, ranks and N=4/6 comparison executed. |
| 10. special-vector identification | verified | 26–33 | Candidate scan and actual sparse search executed at k=1..4; four independent vectors; k=0 empty case. |
| 11. coefficient extraction and closed-form V_k | verified | 34–40 | Labeled numerical and candidate matrices, all-index full reconstruction, final full formula including function terms; exact local proof resolves candidate. |
| 12. symbolic step, base, and boundary identities | verified | 41–50 | Separate symbolic contexts and LHS/RHS identities, exact Gram/function/offset zeros, derived multipliers, sign/domain justification and radius normalization executed. |