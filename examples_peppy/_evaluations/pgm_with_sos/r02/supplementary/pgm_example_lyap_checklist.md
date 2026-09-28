Notebook: pgm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 14f318cae0e634bdf807ee13bd7c96ed1a7f36c133583abf68d794e830a9449e
Presentation policy: evaluation-ancillary-v1. No browser, image inspection or rendered review performed, as required. Markdown delimiter/control-character checks passed; this is source inspection, not rendered verification.
Final validation: supplementary/b5-static-001.json (Ruff and ty passed); supplementary/b5-final-nbconvert-console.txt (fresh-kernel nbconvert execution passed).

| Item | Status | Cells and evidence |
|---|---|---|
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | Cell 0: full assumptions, proximal-gradient update and target metric. |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | Cells 1-3: separate Proof Statement, Theorem and self-contained Proof outline; explicit potential, all residual/SOS definitions and decrement identity, signs and endpoints. |
| 3. imports | verified | Cell 4: executed imports; approved framework origin printed. |
| 4. function/operator definitions | verified | Cell 6: smooth f, closed convex g, sum h, parameters L,R. |
| 5. make_ctx_pgm and get_pep_setup | verified | Cells 6-7: context builder, proximal recurrence, sum stationarity, R**2 constraint and objective gap; executed. |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | Cells 8-10: seven numerical values and statuses; comparison plot preserved as image/png; candidate discrepancy printed. |
| 7. dense and relaxed proof solves | verified | Cells 11-12,19-20: actual dense and sparse solve records at N=4 and N=6, all-owner summaries, preserved bounds and recorded solver statuses. |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | Cells 13-20: rational multiplier/SOS candidate definitions and labeled matrices, complete saved-certificate replay and Gram/function/offset checks; initial formula-search record. Cells 38-53 and proof outline establish final analytic global certificate by exact local telescoping. |
| 9. partial-sum Lyapunov construction and rank profile | verified | Cells 21-24: explicit partial-sum loop, full coverage/PSD-piece/increment checks and rank profile; fixed (1,1) exclusions; rank 4 at N=4,6; recovery and fixed blend disclosed. |
| 10. special-vector identification | verified | Cells 25-31: actual candidate construction/deduplication/column-space scan, sparse-basis search outputs, reproducible templates and every-index independence checks. |
| 11. coefficient extraction and closed-form V_k | verified | Cells 32-38,2-3: labeled numerical and candidate coefficient matrices; full Gram/function/offset reconstruction for every k; explicit closed-form potential; coefficient recurrences and final exact proof resolve candidate status. |
| 12. symbolic step, base, and boundary identities | verified | Cells 39-53: separate symbolic step, base, terminal, exceptional N=1 and radius-normalization identities; actual PEPFlow contexts/recurrence/LHS/RHS/differences. Exact zero Gram matrices and function/offset outputs. Cells 3,52 establish signs/domain and nonincreasing telescope. Cells 54-56 give sharpness. |