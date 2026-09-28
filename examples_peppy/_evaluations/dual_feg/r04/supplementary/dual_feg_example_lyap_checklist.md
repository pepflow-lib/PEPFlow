Notebook: dual_feg_example_lyap.ipynb
Last reviewed block: B5 (complete)
SHA-256: 31bdf34f789458641018e06dab7291ed61c868907c212f3b31df9cc805de6970
Presentation policy: evaluation-ancillary-v1. No rendering/image inspection performed. Markdown delimiter/control-character checks passed; embedded plot output checked structurally.

| Item | Status | Cells | Evidence |
| --- | --- | --- | --- |
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | b1-00 | Problem, all assumptions, metric and actual update equations inspected. |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | b5-top-00 through b5-top-02 | Separate proof statement, theorem with exact potential, and self-contained proof outline including every residual and boundary term. |
| 3. imports | verified | b1-02,b1-03 | Fresh kernel imported the approved framework; final static checks passed. |
| 4. function/operator definitions | verified | b1-05 | Monotone Lipschitz operator and symbolic parameters defined. |
| 5. make_ctx_dual_feg and get_pep_setup | verified | b1-07,b1-08 | Visible actual context builder and initial/metric setup executed. |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | b1-09,b1-10 | Seven optimal values, candidate comparison, and embedded matplotlib plot retained. |
| 7. dense and relaxed proof solves | verified | b2-00,b2-01,b2n8-00,b2n8-01 | Dense and two sparsity trials summarized; coherent N=6 and N=8 certificates replayed. |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | b2-02,b2-03,b2n8-01 | Initial closed-form search, full numerical identity, labeled S and residual matrices, LDL reconstruction, and explicit global formula status. |
| 9. partial-sum Lyapunov construction and rank profile | verified | b3-00 through b3-02 | Visible actual partial-sum loop, all-coordinate coverage and PSD signs, ranks and fixed-exclusion confirmation at N=6,8. |
| 10. special-vector identification | verified | b4-00 through b4-07 | Deduplicated candidate scan, actual anchored sparse search and per-k outputs; uniform basis independently reconstructed. |
| 11. coefficient extraction and closed-form V_k | verified | b4-08 through b4-12,b5-00,b5-01 | Every-index numerical matrices and complete scalar reconstruction; closed form for all L,N established by exact recurrence checks. |
| 12. symbolic step, base, and boundary identities | verified | b5-02 through b5-15 | Separate native symbolic step, base, first/last step, N=1 and boundary checks; every Gram/function/offset residual exactly zero; signs/domain/normalization justified. |

Final execution: supplementary/b5-nbconvert-001-output.txt. Static: supplementary/b5-static-001.json. Presentation override: no rendered/image inspection, exports, or browser use. Final post-execution edits changed only historical Markdown status wording; code hash unchanged.