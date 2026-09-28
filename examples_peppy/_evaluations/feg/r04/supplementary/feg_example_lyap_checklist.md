# Notebook evidence checklist
Notebook: feg_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 0ea7a9ca8f07530a794cbc3ec978e80d0c0e30c8f72ee53a4823a6d8c91b9f33
Presentation: evaluation-ancillary-v1; source math and outputs inspected, no rendering or image inspection performed.

| Item | Status | Cells and evidence |
|---|---|---|
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | 0: assumptions, metric, both algorithm equations and shared first half-step inspected |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1-3: separate Proof Statement, Theorem with potential and bound, self-contained proof outline with base/step/boundary equations |
| 3. imports | verified | 4-5: private approved-root bootstrap and executed imports |
| 4. function/operator definitions | verified | 6: L,R and LipschitzMonotoneOperator |
| 5. make_ctx_feg and get_pep_setup | verified | 7: actual recurrence, tags, shared initial point, squared radius and metric |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 8-10: seven printed SDP values, curve and embedded PNG present; no image inspection under presentation override |
| 7. dense and relaxed proof solves | verified | 11-12: dense and sparse solves, basis, both multiplier families, S eigenvalues and preserved objective |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 13-18: complete selected numerical identity, true S and LDL matrices, reconstruction residuals, initial formula search and honest candidate mismatch/global status |
| 9. partial-sum Lyapunov construction and rank profile | verified | 19-23: certificate reconstruction, whole-S decomposition, visible partial-sum loop and ranks, both-horizon coverage and fixed exclusions |
| 10. special-vector identification | verified | 24-32: real candidate/filter/sparse search with all-index selected bases, zero counts and adopted basis |
| 11. coefficient extraction and closed-form V_k | verified | 33-42: all numerical matrices and full-component reconstruction; unknown coefficient recurrence solved exactly; labeled exact coefficients and numerical differences; closed-form conclusion |
| 12. symbolic step, base, and boundary identities | verified | 43-52: separate symbolic PF step/base/boundary contexts, exact zero Gram/function/offset outputs, LaTeX equations and signs/domain/normalization argument |