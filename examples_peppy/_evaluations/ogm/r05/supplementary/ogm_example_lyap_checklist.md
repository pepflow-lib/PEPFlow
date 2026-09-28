# Notebook evidence checklist

Notebook: ogm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 770db3751c058b2f94f5f23dca8e777dafee878eda9cf8c712e8e90358f5889c
Presentation: evaluation-ancillary-v1. No browser, rendered preview or image inspection; source and executed-output checks only.

| Item | Requirement | Status | Cell indices | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | 0 | All assumptions and all updates, including terminal recurrence, present; source math checks passed. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1-3 | Separate theorem and self-contained proof outline; full potential, all increments, signs, N=1 and final normalization. |
| 3 | imports | verified | 4-5 | Approved import origin asserted and printed in fresh kernel. |
| 4 | function/operator definitions | verified | 6-7 | Smooth convex function and L/R parameters visible. |
| 5 | make_ctx_ogm and get_pep_setup | verified | 8-9 | Actual tagged updates, squared radius and target metric visible and executed. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 10-12 | Seven printed values, residual 3.12e-9, and embedded comparison plot present; no visual inspection performed. |
| 7 | dense and relaxed proof solves | verified | 13-15 | Coherent dense and relaxed state/provenance; complete summaries and preserved-objective check. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 16-22,60 | Initial search, candidate comparisons, labeled matrices, full numerical identity/LDL reconstruction; final global analytic identity by proved telescoping. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | 23-27 | Actual grouping loop, all-coordinate coverage and fixed-exclusion two-horizon rank check; independent saved-source replay also passed. |
| 10 | special-vector identification | verified | 28-36 | Visible candidate scan and actual sparse basis search; all-index independence and reconstruction. |
| 11 | coefficient extraction and closed-form V_k | verified | 37-45 | Labeled numerical and exact coefficient matrices, function terms, full expression reconstruction and resolved formula. |
| 12 | symbolic step, base, and boundary identities | verified | 46-63 | Separate exact zero Gram/function/offset checks, N=1, positive-root/sign proofs, normalization and sharpness. |
