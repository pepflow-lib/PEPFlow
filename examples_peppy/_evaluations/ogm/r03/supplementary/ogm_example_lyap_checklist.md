Notebook: ogm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 44a82dbc9876ae6a302f3ec27091a96cc1a065899417d68a5449cd758e071ab2
Presentation policy: evaluation-ancillary-v1. Source delimiters and controls checked. No browser, rendering or image inspection performed; the frozen override applies.
Static: supplementary/b5-static-002.json; clean kernel: supplementary/b5-final-nbconvert-output-002.txt.

| Item | Requirement | Status | Cells (zero-based) | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Algorithm, smooth-convex assumptions, special terminal theta, radius squared and metric present. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1,2,3 | Separate heading, theorem and proof outline contain explicit potential and detailed decrease/boundary identities. |
| 3 | imports | verified | 4,11,24,38 | Approved source roots and required imports present and executed. |
| 4 | function/operator definitions | verified | 6 | SmoothConvexFunction and L,R definitions visible. |
| 5 | make_ctx_ogm and get_pep_setup | verified | 6 | Context builder and setup interface visibly encode the actual recursion and normalization. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 7,8,9 | Seven optimal numerical values, candidate curve and actual PNG plot output present. |
| 7 | dense and relaxed proof solves | verified | 10,11,12,17,18 | Dense and sparse solve source, saved coherent results, support and preserved optimum displayed; N6 certificate separately retained. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 13,14,15,16,57 | Numerical multipliers, true labeled S, spectral reconstruction, candidate lambda/S displays, full-coordinate residuals and exact global proof present. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | 19,20,21,22 | Actual partial-sum loop, all-coordinate coverage and rank output at N4,N6; fixed exclusions (2,0). |
| 10 | special-vector identification | verified | 23,24,25,26,27,28,29,30 | Deduplicated candidate scan, actual sparse search, adopted local basis and endpoint independence executed. |
| 11 | coefficient extraction and closed-form V_k | verified | 31,32,33,34,39,47,55,56 | All-index numerical matrix and scalar reconstruction; exact coefficient derivation and labeled formula comparisons present. |
| 12 | symbolic step, base, and boundary identities | verified | 40,41,42,43,44,45,48,49,50,51,52,53,54,57 | Separate symbolic contexts construct LHS,RHS,diff; all Gram/function/offset residuals zero. Normalization, N1, sign/domain and telescoping arguments present. |