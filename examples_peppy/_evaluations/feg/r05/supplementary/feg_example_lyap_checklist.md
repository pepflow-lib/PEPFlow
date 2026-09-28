Notebook: feg_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 589213081a76d2eac184feec8c851eed5d32a9e798fcfc0c545c087b061b3e21
Presentation policy: evaluation-ancillary-v1. Executed source/output audit; no rendered/image review performed or claimed.

| Item | Status | Cells and evidence |
|---|---|---|
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | 0: full assumptions, both updates, shared initial half point, metric |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1-3: separate theorem and self-contained detailed proof; explicit potential and exact constant |
| 3. imports | verified | 4,5: approved roots and executable imports |
| 4. function/operator definitions | verified | 7: L-Lipschitz monotone operator, L and R |
| 5. make_ctx_feg and get_pep_setup | verified | 9: actual context builder, initial R squared constraint, terminal squared residual |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 10-12: seven optimal values and saved PNG comparison plot output |
| 7. dense and relaxed proof solves | verified | 13,14,20,21: dense and sparse solve records at N=6,8; support and bound-preservation checks |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 15-19: complete numerical identity and LDL reconstruction, true S and candidate displays, candidate failures and unresolved global status |
| 9. partial-sum Lyapunov construction and rank profile | verified | 22-24: visible source/coordinate replay, actual grouping loop, rank printout, fixed-exclusion N=6,8 comparison and coverage |
| 10. special-vector identification | verified | 25-33: rich candidate scan, actual sparse-basis search output at each index, adopted interpretable template and independence |
| 11. coefficient extraction and closed-form V_k | verified | 34-44: all-index full-coordinate numerical reconstruction, unknown-coefficient elimination, exact recurrence and positive normalization, labeled exact C and comparison |
| 12. symbolic step, base, and boundary identities | verified | 45-55: separate symbolic PEPFlow step/base/boundary identities with labeled zero residuals in all scalar components, complete sign/domain and normalization argument |