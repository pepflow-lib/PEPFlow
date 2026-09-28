Notebook: ogm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 55b3515f90ca678c87e006e79c32674b5e9ec7623a7235758c21cad5192654d8
Presentation policy: evaluation-ancillary-v1. No browser, rendered visual review, screenshot, or image inspection performed. Markdown delimiters/escapes, actual source, printed output and embedded output types inspected. This override does not waive mathematical, static, or execution gates.
Static evidence: supplementary/b5-static-001.json
Clean-kernel execution: supplementary/b5-nbconvert-evidence.json; actual nbconvert --execute exit 0.
Final Markdown-only cleanup preserved executable source hash: supplementary/b5-final-markdown-evidence.json.

| Item | Status | Zero-based cell indices | Evidence |
|---|---|---|---|
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Assumptions, exact algorithm, initial condition, metric and special terminal theta recurrence inspected. |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1-3 | Placeholder replaced by separate heading, theorem with full V formula and terminal case, and self-contained proof with every local residual and sign implication. |
| 3. imports | verified | 4-5 | Pinned runtime and approved framework origin printed; private cache and numerical thread configuration retained. |
| 4. function/operator definitions | verified | 6-7 | Convex L-smooth function and L,R parameters visibly defined. |
| 5. make_ctx_ogm and get_pep_setup | verified | 8-9 | Visible context builder, every update/tag, stationary point, R-squared constraint, and objective-gap metric. |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 10-12 | Seven actual optimal CLARABEL sweep rows and candidate comparison printed; PNG plot embedded. Plot data inspected without viewing an image. |
| 7. dense and relaxed proof solves | verified | 13-14 | Actual dense/sparse acquisition evidence preserved, active pairs summarized, matching bound checked; one coherent sparse certificate used. |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 15-17 | All-coordinate certificate replay, scalar signs/PSD, sparse-lambda candidate matrix, true S and reconstruction displays; original formula search and separate global analytic status retained. Independent N=6 replay included. |
| 9. partial-sum Lyapunov construction and rank profile | verified | 18-23 | Visible extraction, S pieces, lyap/partial_sum loop, rank printouts and coverage checks. Independent N=4,6 samples confirm rank 3 under fixed (1,1) exclusions and threshold 1e-4. |
| 10. special-vector identification | verified | 24-32 | Rich deduplicated candidate scan and actual sparse-basis search executed for each nonzero-rank index; selected pattern and endpoint exception stated. |
| 11. coefficient extraction and closed-form V_k | verified | 33-42 | Labeled numeric and candidate matrices, every-index independence/quadratic/function/offset reconstruction, coefficient derivation and complete general-L formula inspected; exact verification below establishes it. |
| 12. symbolic step, base, and boundary identities | verified | 43-57 | Separate native PEPFlow contexts and LHS/RHS/diff calculations; all Gram/function/offset components exactly zero for ordinary/base/terminal/metric/N=1/normalization. Equation cells immediately follow verification headings; signs/domain/telescoping complete. |