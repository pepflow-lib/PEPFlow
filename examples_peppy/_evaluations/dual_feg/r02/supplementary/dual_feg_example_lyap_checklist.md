Notebook: dual_feg_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 1f8fb8e949620e62b837b45ce1c0bb125de2d2b55ac617d13729e13203caffef
Presentation: evaluation-ancillary-v1. No browser, rendering, or image inspection. Required code execution and source-math checks passed; PNG presence verified only.

| Item | Status | Cells (zero-based) | Evidence |
|---|---|---|---|
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Assumptions, all three updates, metric and horizon explicitly present. |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1–3 | Separate theorem/outline; full closed form and all residual identities with signs and radius normalization. |
| 3. imports | verified | 4–5 | Approved source origin asserted; fresh kernel passed. |
| 4. function/operator definitions | verified | 6 | LipschitzMonotoneOperator and symbolic parameters visible. |
| 5. make_ctx_dual_feg and get_pep_setup | verified | 7 | Actual recursion, tags, initial radius squared and terminal residual visible. |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 8–9 | Seven printed values, statuses and PNG comparison plot; N=1 status retained. |
| 7. dense and relaxed proof solves | verified | 10–11 | Dense, threshold and structural sparse summaries; preserved optimum. |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 12–14 | Complete numerical Gram/function/offset check; true S, factors and candidates labeled; global analytic status distinct. |
| 9. partial-sum Lyapunov construction and rank profile | verified | 15–20 | Visible accumulation and step assignments; rank 4 confirmed at N=4,6; coverage and sign checks. |
| 10. special-vector identification | verified | 21–28 | Visible candidate filtering and actual sparse search per k; clear adopted pattern and independence. |
| 11. coefficient extraction and closed-form V_k | verified | 29–35, 38 | All-index numerical matrices and components; final general-L expression and exact representation check. |
| 12. symbolic step, base, and boundary identities | verified | 36–50 | Executed symbolic step/base/final/boundary/N=1; zero Gram/function/offset residuals; signs and domains established. |