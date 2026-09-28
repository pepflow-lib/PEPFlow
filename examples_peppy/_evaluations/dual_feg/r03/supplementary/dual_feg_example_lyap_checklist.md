Notebook: dual_feg_example_lyap.ipynb
Last reviewed block: B5
SHA-256: dfe5612a0bfcb822d785b682933ab32d91ac69e821fed4ed2b52913c2f63d3b2

Presentation policy: evaluation-ancillary-v1. Rendering/image inspection was not performed and is not a completion gate. Source formulas, all execution outputs, plot presence, Markdown delimiters and control characters were checked.

| Item | Requirement | Status | Cell indices | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Assumptions, selected metric and all recurrence equations inspected in saved Markdown. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 2,3 | Separate theorem and self-contained proof outline include full potential, residual families, signs, endpoints and exact rate. |
| 3 | imports | verified | 5 | Pinned-source imports executed in fresh kernel. |
| 4 | function/operator definitions | verified | 7 | Monotone Lipschitz operator and symbolic parameters present and executed. |
| 5 | make_ctx_dual_feg and get_pep_setup | verified | 9 | Visible exact-ratio algorithm, z0, zero point, squared radius and final-residual metric executed. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 12 | N=1..7 cached numeric values and comparison curve printed; executed PNG plot retained; N=2 solver status disclosed. |
| 7 | dense and relaxed proof solves | verified | 15,17 | Dense and both sparse discovery solves retained; selected support and preserved optimum inspected; additional N6 sample verified. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | ,23,25 | Actual lambda/S checks, full numerical LDL decomposition, true S and candidate displays, initial search, exact global telescoping argument inspected. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | 32 | Visible partial-sum loop, all contribution assignments, sign/coverage checks and same-recipe N4/N6 rank confirmation executed. |
| 10 | special-vector identification | verified | 38,40,42 | Visible framework sparse-basis search with per-index outputs, adopted basis independence, every-index full-component reconstruction executed. |
| 11 | coefficient extraction and closed-form V_k | verified | 45,51 | Labeled numerical/candidate matrices and complete potential present; symbolic identities prove candidate coefficients for all claimed horizons. |
| 12 | symbolic step, base, and boundary identities | verified | 55,58,61,64,67 | Separate symbolic step, base, terminal, N1 and radius-boundary checks execute; six exact Gram/function/offset checks pass; signs/domain/normalization proof inspected. |