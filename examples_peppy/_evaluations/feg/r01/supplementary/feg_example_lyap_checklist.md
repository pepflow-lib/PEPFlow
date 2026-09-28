Notebook: feg_example_lyap.ipynb
Last reviewed block: B5
SHA-256: aaa76fa4c97a57d0ce072c020dbe62436d980b0751872ed770c0d39a569dd6da
Presentation policy: evaluation-ancillary-v1; no rendered/image inspection. All required mathematical/source/execution checks performed.

| # | Item | Status | Cells | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | b1-00, proof-01 | Assumptions, residual metric, both recurrences, initial half-step sharing and domains present. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | proof-00 through proof-02 | Separate theorem and self-contained proof outline give explicit V, base/step/boundary equations and bound. |
| 3 | imports | verified | b1-02, b1-03, b4-01, b5-01 | Approved paths, framework, symbolic/numerical and plotting imports execute in fresh kernel. |
| 4 | function/operator definitions | verified | b1-03 | Monotone Lipschitz class with L,R parameters; symbolic contexts use distinct operator tags. |
| 5 | make_ctx_feg and get_pep_setup | verified | b1-04 | Visible executable recursion, radius-squared initial condition and final residual metric. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | b1-05,b1-06 | All seven values and image/png comparison plot are present; no image inspection per presentation override. |
| 7 | dense and relaxed proof solves | verified | b2-01,b2-02 | Actual saved dense/sparse results, visible acquisition/support recipe, preserved-bound check, labeled active multipliers. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | b2-03 through b2-08 | Initial candidate search failures explicit; true S, full LDL, labeled coordinate residuals and separate global analytic status retained. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | b3-00 through b3-04 | Visible complete certificate replay, grouping/update loop, per-index ranks, N=4/6 comparison and full coverage/sign checks. |
| 10 | special-vector identification | verified | b4-00 through b4-07 | 342 candidate scan, actual sparsity-search outputs for every nonzero k, adopted meaningful basis and endpoint independence. |
| 11 | coefficient extraction and closed-form V_k | verified | b4-08 through b4-11, b5-02 through b5-06 | All numerical matrices/components reconstructed; symbolic recurrence solves unknowns, scale choice explicit, exact coefficient matrices and closed form displayed. |
| 12 | symbolic step, base, and boundary identities | verified | b5-07 through b5-17 | Separate native PEPFlow symbolic identities, all Gram/function/offset residuals zero, labeled matrices, signs/domain/normalization and N=1 covered. |
