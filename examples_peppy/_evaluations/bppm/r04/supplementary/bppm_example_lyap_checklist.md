Notebook: bppm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 48109a7cb86042a6941cf72725fd80c89315310a6fcab14e7bdb37ff8bda6f3b
Presentation policy: evaluation-ancillary-v1. Source, outputs, delimiters and execution inspected. No rendering, browser, or image inspection performed; no rendered-review claim.

|Item|Requirement|Status|Cell indices|Evidence|
|---|---|---|---|---|
|1|title, problem description, and the algorithm update equations in LaTeX|verified|0|All assumptions, Bregman definition, exact updates and metric inspected.|
|2|proof statement placeholder, to be filled with the final theorem and proof outline in Block 5|verified|1,2,3|Placeholder replaced by separate proof heading, self-contained theorem and detailed outline with full V_k, all residuals and bound.|
|3|imports|verified|4,5,13,22,26,38|Pinned approved source paths and private runtime; final fresh kernel execution passed.|
|4|function/operator definitions|verified|7|Both convex function families, alpha and R definitions inspected.|
|5|make_ctx_bppm and get_pep_setup|verified|8|Actual proximal recurrence, initial radius R, and metric visible and executable.|
|6|numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate|verified|10|Seven optimal CLARABEL values, printed comparison and embedded PNG plot verified as output; no image inspection under policy.|
|7|dense and relaxed proof solves|verified|12,13,14,19,20|Complete coherent N4 and N6 solve provenance, active groups, relaxation and preserved-optimum output inspected.|
|8|lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)|verified|15,16,17,18|Initial formula search, labeled candidates/actual S, full eigendecomposition reconstruction and all-coordinate numerical certificate checks present; global analytic status explicitly false.|
|9|partial-sum Lyapunov construction and rank profile|verified|21,22,23|Actual construction loops, all certificate/grouping checks, singular-value credibility, and rank4 at N4/N6 with fixed exclusions (1,1) executed.|
|10|special-vector identification|verified|24,25,26,27,28,29,30,31|Actual deduplicated candidate scan, column filtering and sparse search outputs for every nonzero index; boundary independence verified.|
|11|coefficient extraction and closed-form V_k|verified|32,33,34,35,36,37,41|All-index labeled coefficient matrices, comparisons, full-expression reconstructions and exact coefficient-structure identity; function gaps and zero offset retained.|
|12|symbolic step, base, and boundary identities|verified|38,39,40,41,42,43,44,45,46,47,48,49,50|Separate auxiliary PEPFlow contexts and visible LHS/RHS/difference calculations; all Gram/function/offset residuals exactly zero; sign, domain, N1, R0 and normalization arguments inspected.|