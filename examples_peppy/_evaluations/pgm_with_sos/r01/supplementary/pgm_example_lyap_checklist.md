Notebook: pgm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 9a5dfed9ed1618e6992b0a4a1b65c201e602bfd8dd90f7989aa1a879fdd2b6e9
Presentation policy: evaluation-ancillary-v1; source checks complete. Rendering and image inspection omitted as required; no rendered-verification claim.

| # | Item | Status | Cells (zero based) | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Assumptions, metric and recurrence present; source delimiters and escapes checked. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1,2,3 | Separate heading, theorem including full potential and self-contained proof outline with every local multiplier and square. |
| 3 | imports | verified | 4,13,20,27,32 | Pinned kernel imported approved framework and private helpers; numerical and symbolic imports executed. |
| 4 | function/operator definitions | verified | 5 | Smooth convex f, convex g, h=f+g and symbolic L,R defined. |
| 5 | make_ctx_{ALGO_NAME} and get_pep_setup | verified | 6 | Proximal update, optimum stationarity, radius constraint and objective implemented and replayed. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 7,8 | Seven saved PEP values and comparison plot retained; PNG output existence checked without image inspection. |
| 7 | dense and relaxed proof solves | verified | 9,10 | Dense and relaxed solve summaries, coherent certificate matrices and metadata replayed. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 11-14 | Initial candidate search, numerical complete certificate, matrix labels, signs, SOS reconstruction, source hashes and exact fixed-N check retained. Global analytic formula explicitly unverified. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | 15,16 | Explicit partial_sum and lyap construction, verified PSD allocation, ranks 4 at N4/N6 with exclusions (1,1), coverage checked. |
| 10 | special-vector identification | verified | 17-25 | Actual per-index sparse basis search, candidate filtering, selected coefficients and uniform basis verified. |
| 11 | coefficient extraction and closed-form V_k | verified | 26-35 | All-index numeric coefficient extraction and labeled matrices; exact formulas, function gaps, zero offset, all-component coefficient equations and unique solution. Analytic comparison maximum 9.579e-6. |
| 12 | symbolic step, base, and boundary identities | verified | 36-49 | Separate native symbolic step/base/boundary contexts plus N=1. Every Gram/function/offset residual exactly zero; labeled residuals retained. Signs, domains and LR^2/(4N) normalization established. |

Static evidence: supplementary/b5-static-001.json. Final clean-kernel nbconvert execution: supplementary/b5-nbconvert-001-output.txt (exit 0). Harmless Windows event-loop/comm warnings retained; duplicate auxiliary-context labels emitted warnings without failed checks.
