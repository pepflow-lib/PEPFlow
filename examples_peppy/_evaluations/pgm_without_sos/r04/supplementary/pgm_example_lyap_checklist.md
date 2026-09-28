Notebook: pgm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 910087c97115f663c2292c16ae8bf9e137862444295343769300891c5434cd26
Presentation policy: evaluation-ancillary-v1. Rendering/image inspection intentionally not performed; no rendered-review claim. Source delimiters/control characters and all required executed outputs inspected.

| # | Item | Status | Cells (zero-based) | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Assumptions, recurrence, proximal optimality and composite metric present; source delimiters checked. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1–3 | Replaced by separate proof-statement heading, full Lyapunov theorem with finite-product coefficients, and self-contained detailed proof. |
| 3 | imports | verified | 4–5 | Approved framework origin asserted; pinned clean kernel executed. |
| 4 | function/operator definitions | verified | 6–7 | Smooth convex f, closed proper convex g, sum stationarity and parameters visible. |
| 5 | make_ctx_pgm and get_pep_setup | verified | 8–9 | Actual proximal recursion, squared-radius constraint and composite objective visible and executable. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 10–12 | N=1..7 results and statuses printed; maximum candidate discrepancy 4.3191076e-9; comparison plot embedded. |
| 7 | dense and relaxed proof solves | verified | 13–14 | Complete captured dense and sparse solves, both function groups, coordinate basis and preserved optimum displayed; provenance/state retained. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 15–19 | Candidate multipliers, labeled true S and LDL matrices, reconstruction and Gram/function/constant identities present. Initial formula search retained; global analytic full-PEP status remains unverified. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | 20–26 | Full replay, visible partial-sum loop, all-coordinate coverage, signs and rank4 confirmation at N=4,6; fixed exclusions (1,1), absolute tolerance1e-4, singular-value evidence retained. |
| 10 | special-vector identification | verified | 27–35 | Actual candidate generation/filtering, executable sparsity search and per-index output, adopted basis and endpoint independence checks. |
| 11 | coefficient extraction and closed-form V_k | verified | 36–45 | Numerical labeled matrices and complete expression reconstruction at all indices; exact transfer-product solution and recurrence derivation; all sample coefficient comparisons pass. |
| 12 | symbolic step, base, and boundary identities | verified | 46–61 | Separate symbolic PEPFlow step/base/terminal/normalization/N=1 contexts and all-coordinate exact-zero outputs; domain/sign proof and final telescoping present. |
