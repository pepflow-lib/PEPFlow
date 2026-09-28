# Notebook evidence checklist

Notebook: bppm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 52f27a4cc4192211d3704cf8260f16ea9dc31a5fee73c7acc71ef1a4a9f272dd

Presentation policy: evaluation-ancillary-v1. Source delimiters, control characters, executable content and saved outputs inspected. No browser, rendering or image inspection performed or claimed.

| Item | Requirement | Status | Cell indices | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Assumptions, Bregman orientation, update, metric, and unsquared radius inspected. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1-3 | Separate Proof Statement, Theorem, and self-contained Proof outline with explicit potential, full decrease equation, signs and terminal normalization. |
| 3 | imports | verified | 4,5 | Approved source and own helper origin checked; fresh kernel execution. |
| 4 | function/operator definitions | verified | 6,7 | Convex f and h and parameters visible; no extra curvature assumption. |
| 5 | make_ctx_{ALGO_NAME} and get_pep_setup | verified | 8-10 | Actual proximal update, tags, initial Bregman condition and terminal metric visible and executed. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 11-13 | Seven values, inverse-difference pattern, error check and comparison PNG output present. Rendering not inspected under evaluation policy. |
| 7 | dense and relaxed proof solves | verified | 14-16,25-26 | Complete same-solve provenance, active groups, dense/sparse bound comparison; independent N=6 certificate checks. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 17-24 | Initial search record, candidate matrices, true S, retained factor reconstruction and all-coordinate numerical residual checks. Independent global analytic status explicitly unverified. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | 27-33 | Exact executed grouping shown; all terms assigned; PSD boundary piece retained; full-coordinate coverage checked; rank 4 at N=4,6 with fixed exclusions. |
| 10 | special-vector identification | verified | 34-42 | Actual column-space filter and sparse search, executed at every nonzero index; independent four-vector basis and empty k=0 basis. |
| 11 | coefficient extraction and closed-form V_k | verified | 43-50,55 | Labeled numerical and candidate coefficient matrices, function coordinates, full-expression reconstruction at every index, and exact symbolic coefficient-structure verification. |
| 12 | symbolic step, base, and boundary identities | verified | 51-62 | Separate symbolic contexts and visible LHS/RHS/diff; exact Gram/function/offset checks; local signs, domain, N=1, and radius normalization proved. |
