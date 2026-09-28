Notebook: pgm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 6ae3202fcf3fc3b043416caca478059e1cb4e552a4768ca6e38c4e770e5881dd
Presentation policy: evaluation-ancillary-v1. No rendering or image inspection. Verified means source/content, stored mathematical outputs and execution checks under that override. Markdown row breaks, braces, delimiters and control characters audited.

| Item | Requirement | Status | Cell indices | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | 0 | All assumptions, metric, update and proximal optimality condition in source. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1,2,3 | Placeholder replaced with theorem, explicit finite-product potential and self-contained local identities, signs and telescope. |
| 3 | imports | verified | 4,5 | Approved path and pinned fresh kernel executed. |
| 4 | function/operator definitions | verified | 6 | Smooth convex f, convex g and composite h exposed. |
| 5 | make_ctx_pgm and get_pep_setup | verified | 6 | Context construction, actual recursion, squared-radius constraint and metric exposed. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 7,8,9 | Seven printed values and image/png plot output retained; N6/N7 inaccurate statuses disclosed. No image inspection. |
| 7 | dense and relaxed proof solves | verified | 10,11 | Both N4 solves retained with active groups, sparse support, objective comparison; N6 additional sample disclosed. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 10,11 | Complete coherent certificate identity, sign/PSD checks, labeled true S and factor D, reconstruction, and initial candidate search. Separate global analytic status remains false. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | 12,13 | Visible saved-certificate checker, LDL decomposition, grouping and accumulation loops; ranks at both horizons; all components covered. |
| 10 | special-vector identification | verified | 14-21 | Visible actual sparse-basis search with outputs, consistent adopted template, endpoint and independence checks. |
| 11 | coefficient extraction and closed-form V_k | verified | 22-31 | All-index full-expression reconstruction; labeled coefficient and formula-comparison matrices; exact finite-product formula, recurrence derivation and arbitrary-horizon product argument. |
| 12 | symbolic step, base, and boundary identities | verified | 32-45 | Distinct symbolic PEPFlow contexts: generic step, base, terminal, N1; exact Gram/function/offset residuals; signs, nonzero denominators, and radius normalization. |