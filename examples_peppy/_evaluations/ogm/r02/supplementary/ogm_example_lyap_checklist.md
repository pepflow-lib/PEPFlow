Notebook: ogm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 96476335014518f5dce2103dfe69dbf8b7e89a40040dad99efbb9fe25f23fa78
Presentation policy: evaluation-ancillary-v1. Source and executed outputs inspected; browser/rendered/image inspection omitted under the frozen policy.

| # | Required item | Status | Cells | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | b1-algorithm | Source reviewed: complete assumptions, metric, updates and special terminal theta recurrence. Delimiters and control characters checked. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | proof-heading, proof-theorem, proof-outline | Placeholder replaced with separate heading/theorem/proof cells; explicit complete V formula, all local residual identities, signs, N=1, and rate implication. |
| 3 | imports | verified | b1-imports | Fresh-kernel assertion confirms approved framework origin; required static checks passed. |
| 4 | function/operator definitions | verified | b1-functions | Smooth convex function and L/R parameters visible and executed. |
| 5 | make_ctx_ogm and get_pep_setup | verified | b1-setup, b1-setup-check | Visible recurrence, theta construction, initial radius squared, stationary optimum, terminal metric; executed context. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | b1-evidence | Seven numerical values and image/png comparison output present; error 3.1168371598944145e-09. Plot not visually inspected under policy. |
| 7 | dense and relaxed proof solves | verified | b2-load-summary | Both coherent captures retained, actual sparse relaxation reconstructed and dense/relaxed gap checked; solver/settings visible. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | b2-candidates, b2-certificate-check | Initial formula search and numerical candidates preserved; complete numerical inventory/identity/PSD/LDL checks and labeled matrices executed. Separate global analytic certificate remains unverified. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | b3-decomposition, b3-partial-sums, b3-cross-horizon | Actual signed partial-sum loop, whole PSD boundary S, all-component coverage, fixed exclusions (1,1), rank-three interiors at N=6,8 and singular-value evidence. |
| 10 | special-vector identification | verified | b4-candidate-build, b4-candidate-filter, b4-search, b4-basis | 392 distinct nonzero candidates; actual sparse search and its per-index outputs visible; independent interior and terminal bases; empty base handled. |
| 11 | coefficient extraction and closed-form V_k | verified | b4-extract, b4-fit, b4-conclusion, b5-formula, proof-theorem | Numerical all-index extraction and full-expression reconstruction; complete exact coefficients established by B5 identities, including function gaps and terminal case. |
| 12 | symbolic step, base, and boundary identities | verified | b5-step, b5-base, b5-terminal, b5-boundary, b5-small, b5-domain, b5-signs | Actual symbolic PEPFlow contexts and LHS/RHS checks executed. Every Gram/function/offset residual exactly zero; recurrence positivity, nonincreasing direction, radius normalization and N=1 established. |
