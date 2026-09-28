# Notebook evidence checklist
Notebook: bppm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 6335778846aa3879d9445cf98e50ebc21162ae14139cd268ffd2fd12a12d4fbf
Presentation policy: evaluation-ancillary-v1. No browser, rendering or image inspection performed. Source math, saved text outputs and output metadata inspected; required final fresh-kernel nbconvert execution and static checks passed.

| Item | Status | Cells | Evidence |
|---|---|---|---|
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | 0 (0f5e5529) | Problem, assumptions, metric and Bregman proximal update visibly stated. |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1 (1e178a91), 2 (16088153), 3 (31a67515) | Separate heading/theorem/proof cells; full V_k, all four step residuals, base, boundary, signs and exact R/(alpha N) normalization. |
| 3. imports | verified | 4 (6981b247), 5 (40276be3) | Approved imports and private runtime paths execute; actual framework origin printed. |
| 4. function/operator definitions | verified | 7 (5f0b8877) | Two convex function definitions and alpha/R parameters visible. |
| 5. `make_ctx_{ALGO_NAME}` and `get_pep_setup` | verified | 9 (c21c2aa1) | Actual proximal iteration, initial Bregman constraint and final objective metric visible. |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 10 (433ab120), 11 (4666f2d1), 12 (64e7fe35) | Seven optimal CLARABEL values, inverse-rate increments, maximum discrepancy 3.622e-9, and stored matplotlib comparison plot. |
| 7. dense and relaxed proof solves | verified | 13 (46ea28c6), 14 (424b28e7) | Both dense and sparse solve outputs, all active owner groups, basis and preserved bound displayed. |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 13 (46ea28c6), 15 (435c6034) | Actual S matrix and complete spectral decomposition; all multiplier signs and Gram/function/offset identities checked; initial candidate search and separately unverified global analytic status recorded. |
| 9. partial-sum Lyapunov construction and rank profile | verified | 16 (5bc46639), 17 (f15f284d), 18 (cbda04d1), 19 (8a508400), 20 (2d14274b), 21 (1095f4fe) | Selected numerical certificate revalidated; visible partial sums; ranks and full-coordinate coverage; fixed (1,1) exclusions confirm rank 4 at N=4 and N=6. |
| 10. special-vector identification | verified | 22 (cb22dc32), 23 (ba40f5a0), 24 (b7e46121), 25 (ceb05507), 26 (9633ea4c), 27 (0436df0c), 28 (936fc64e), 29 (36bbadc4) | Actual candidate scan and sparse subset search executed, selected bases and zero counts printed; independence checked for all indices including endpoints. |
| 11. coefficient extraction and closed-form `V_k` | verified | 30 (b81da4f4), 31 (9ca4af50), 32 (f7af2fb8), 33 (5310314e), 34 (ccd38a8e), 35 (1e6f87ad), 36 (1d24a99d), 37 (538516a7) | All-index numerical matrices and full function/offset reconstruction, candidate fits, exact coefficient recurrence solution and final closed form including function gaps. |
| 12. symbolic step, base, and boundary identities | verified | 38 (750d8d0a), 39 (688083a7), 40 (22825051), 41 (e9ef9d4c), 42 (c5268d80), 43 (c4b49ec5), 44 (9ac7c917), 45 (a7916fb6), 46 (e1056de2), 47 (b825a3cf), 48 (f5f719fb) | Separate symbolic PEPFlow step/base/terminal contexts; all Gram/function/offset residuals zero with labeled matrices; N=1/R=0 coverage; signs/domain/normalization established. |