Notebook: feg_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 4a58a52bee0659843d299119b4e440b3defbe44c21e8609ff2c4d811aab856ce
Presentation policy: evaluation-ancillary-v1. Source math delimiters and control characters checked; executed plot/matrix outputs retained. No rendering, image inspection, or visual verification was performed or claimed.

| Item | Requirement | Status | Cell indices | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Assumptions, exact two-step updates and shared initial half-step inspected in source. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1–3 | Replaced by separate proof heading, theorem with exact V_k, and self-contained base/step/boundary proof. |
| 3 | imports | verified | 4,5 | Final kernel prints approved framework import origin; private pinned kernel used. |
| 4 | function/operator definitions | verified | 6,7 | LipschitzMonotoneOperator with L and radius parameter; final execution passed. |
| 5 | make_ctx_feg and get_pep_setup | verified | 8–10 | Actual recurrence, R squared initial constraint, final residual metric, shared initial point assertion. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 11–13 | Seven printed optimal values and image/png plot output; initial discrepancy explicitly explained. |
| 7 | dense and relaxed proof solves | verified | 14,15,17,21,22 | Dense and sparse sampled solves with complete saved coherent certificates; N6 selected and N8 confirmation. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 16–20,25 | Full numerical identities, labeled matrices, LDL reconstruction, mandatory initial formula search and unresolved global analytic status. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | 23–29 | Visible full certificate replay and grouping loop; coverage, nonincreasing signs and rank two at N6/N8 verified. |
| 10 | special-vector identification | verified | 30–38 | Candidate generation/filter and actual sparse basis search with per-index outputs; common residual/anchor basis independence verified. |
| 11 | coefficient extraction and closed-form V_k | verified | 39–47,50,51 | All-index numerical matrices and full reconstruction; exact coefficient equations solved; labeled analytic matrix and honest numerical discrepancy comparisons. |
| 12 | symbolic step, base, and boundary identities | verified | 48–58 | Separate visible PEPFlow symbolic LHS/RHS/diff constructions, zero Gram/function/offset outputs; domain, sign and full radius normalization proof. |