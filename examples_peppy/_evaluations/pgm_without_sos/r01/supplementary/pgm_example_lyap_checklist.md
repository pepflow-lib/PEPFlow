Notebook: pgm_example_lyap.ipynb
Last reviewed block: B5 complete
SHA-256: eaff34082b79533ac99c272e01816e122e03d16e50b863e6fc08ec2752a4dbe0
Presentation: evaluation-ancillary-v1. Source and saved execution outputs inspected; no rendered/image inspection performed.

| Item | Status | Cells (zero-based) | Evidence |
| --- | --- | --- | --- |
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Source contains all assumptions, proximal recurrence, initial condition, and metric. |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1-3 | Separate heading, theorem with full potential and all endpoint cases, self-contained proof outline with every residual and square. |
| 3. imports | verified | 4-5 | Approved framework origin checks and fresh private kernel execution passed. |
| 4. function/operator definitions | verified | 7 | Smooth convex f, convex g, L and R, composite stationarity. |
| 5. make_ctx_pgm and get_pep_setup | verified | 9 | Executable algorithm, initial normalization and final metric remain visible. |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 10-11 | Seven numerical values/statuses, inverse-rate discovery, error 4.32e-9, PNG output retained; no image inspection under override. |
| 7. dense and relaxed proof solves | verified | 13-17 | Acquisition code, saved dense/selected statuses and coherent certificate replay retained. Dense/relaxed gap 2.34e-10. |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 18-22 | Initial rational formula search, all numerical duals/extras, S/LDL labeled displays and full-coordinate identity checks. Global analytic status explicitly unresolved; local analytic proof separately completed. |
| 9. partial-sum Lyapunov construction and rank profile | verified | 23-27 | Actual partial_sum construction; congruence decomposition covers saved S to roundoff; unchanged rank threshold confirms interior rank 4 at N=4 and N=6 with fixed exclusions (1,1). |
| 10. special-vector identification | verified | 28-36 | Actual sparse basis search executed at every required index; rank, basis and near-zero counts printed. Terminal basis verified after congruence recovery. |
| 11. coefficient extraction and closed-form V_k | verified | 37-46 | Labeled numerical and exact coefficient matrices; function/offset reconstruction; native unknown-coefficient equations and selected exact solution; closed-form conclusion includes function gaps and endpoints. |
| 12. symbolic step, base, and boundary identities | verified | 47-64 | Positive-polynomial sign identities (49); separate native step (52), base (55), terminal (58), N=1 (61) all zero in Gram/function/offset. Normalization and nonincreasing telescoping (62-63); durable B5 state (64). |

Required static checks: b5-static-006.json passed. Final fresh-kernel nbconvert execution: b5-final-notebook-004.txt passed. Proof and source audit: final-audit.json. No tolerances were relaxed.
