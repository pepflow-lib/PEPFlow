Notebook: dual_feg_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 25b4570a98c8cb3157fb46bd558009624629e660cb242cce2042c5432afc9b87
Presentation policy: evaluation-ancillary-v1. Markdown delimiters/control characters checked. Rendering and image inspection omitted under the explicit evaluation override; no rendered verification claimed.
Static checks: supplementary/b5-static-003.json. Clean-kernel nbconvert execution: supplementary/b5-final-execution-002.json.

| Item | Status | Cells (zero-based) | Evidence |
|---|---|---|---|
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Assumptions, metric and three algorithm updates present. |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1,2,3 | Separate proof heading, theorem with full V_k and self-contained detailed proof outline present. |
| 3. imports | verified | 4,5 | Approved source/runtime paths; fresh-kernel execution succeeded. |
| 4. function/operator definitions | verified | 6 | Lipschitz-monotone operator and L,R defined. |
| 5. make_ctx_dual_feg and get_pep_setup | verified | 7 | Visible exact recursion, tags, R^2 constraint and residual metric. |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 8,9 | Seven values/statuses and image/png comparison plot present. |
| 7. dense and relaxed proof solves | verified | 10-14 | Dense and sparse coherent solves at N=6; N=8 confirmation certificate. |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 10-14 | All dual groups, labeled true numerical S, complete LDL factors, candidate formulas and residual matrices; numerical checks passed; global analytic status remains explicit. |
| 9. partial-sum Lyapunov construction and rank profile | verified | 15-20 | Visible full-coordinate certificate replay and partial-sum loop; rank4 at N=6 and N=8 with fixed exclusions; coverage verified. |
| 10. special-vector identification | verified | 21-29 | Actual filtered candidate scan and sparse search output; adopted interior/endpoint bases verified. |
| 11. coefficient extraction and closed-form V_k | verified | 30-38 | All-index numerical coefficients and component reconstruction; exact solved coefficient family, labeled formula matrices and complete closed-form V_k. |
| 12. symbolic step, base, and boundary identities | verified | 39-50 | Separate exact step, initial, final-step, N=1 and performance-boundary contexts; Gram/function/constant residuals zero; signs, domains and normalization justified. |