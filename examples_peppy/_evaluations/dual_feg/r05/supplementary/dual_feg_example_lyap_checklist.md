# Evidence checklist
Notebook: dual_feg_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 0fa0f1eb429ab3c3f080b46c76e4eda913a0ef2937fe826296ab126b8f3684fd
Presentation policy: evaluation-ancillary-v1. Source, equations and saved outputs inspected; no browser, rendering or image inspection was performed.

| Item | Status | Cell indices and IDs | Evidence |
|---|---|---|---|
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | 0:1dccfeb1 | Assumptions, initial condition, metric and all three algorithm recurrences. |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1:0a905577, 2:3d730dab, 3:7dc95847 | Separate theorem and self-contained proof outline; explicit potential, all step residuals, endpoint and rate proof. |
| 3. imports | verified | 4:89d5a523, 5:b8883e5d | Pinned approved imports; executed origin output. |
| 4. function/operator definitions | verified | 7:4a9a3b60 | Lipschitz-monotone operator and parameters. |
| 5. make_ctx_dual_feg and get_pep_setup | verified | 9:185ccb8d, 10:8bdb5170 | Executable context builder and metric/initial-condition setup; zero initialization checked. |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 12:9f2f85a5, 13:ff00a41e | Seven observed values, solver statuses, rate comparison and image/png plot output. |
| 7. dense and relaxed proof solves | verified | 14:84b82515, 15:fed8b292 | Dense and selected sparse solves, preserved bound, every group summarized and labeled numerical dual tables. |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 16:a42bb534, 17:bfe44151, 18:f6ca940f, 19:aa235abb, 20:8aa98d8f, 21:c424d600 | Initial formula search, all selected multipliers, candidate comparisons, true S matrix, complete LDL reconstruction and full-coordinate certificate residuals; global analytic status explicit. |
| 9. partial-sum Lyapunov construction and rank profile | verified | 22:89f628cc, 23:a6cc175e, 24:82aa7b96, 25:a721aaa4, 26:59b6abfe | Visible actual partial-sum loop, all-coordinate certificate/coverage checks, nonincreasing direction, rank four at N=6,8 with fixed exclusions. |
| 10. special-vector identification | verified | 27:5fa38c90, 28:9d0b9fab, 29:d7b906f2, 30:13ce4f3f, 31:21e874a7, 32:8c17312a, 33:895bd265, 34:8ab3bb33, 35:fe66b9a7 | Labeled candidate scan, actual sparse-basis search and zero-count outputs, adopted basis and independence including endpoints. |
| 11. coefficient extraction and closed-form V_k | verified | 36:02878ead, 37:dc53e87a, 38:53132baf, 39:72dd0045, 40:a4c7b796, 41:1658eeae, 42:246333f4, 43:72477b9a | All-index coefficient reconstruction and candidate comparisons; labeled exact coefficient matrix and final formula with general L. |
| 12. symbolic step, base, and boundary identities | verified | 44:3eaf40a0, 45:5be14500, 46:76c36d51, 47:ff57ccfe, 48:00ca33e2, 49:300df1c9, 50:efa7d221, 51:f386bdb3, 52:6199a679, 53:bcb86528, 54:1375a697, 55:8a0671b6, 56:d9a96209, 57:06b04a0a, 58:9ec065ad | Separate exact PEPFlow step, base, final-step and metric-boundary identities with labeled residual matrices and zero function/constant residuals; domain, signs and normalization established. |