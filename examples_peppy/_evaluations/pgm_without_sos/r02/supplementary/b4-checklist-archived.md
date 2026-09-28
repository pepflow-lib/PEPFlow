# Notebook evidence checklist

Notebook: pgm_example_lyap.ipynb
Last reviewed block: B4
SHA-256: 5d7e9f9920b1c93db946fc8df1e17f016276c62cbc18c03eecf2f155093c6282
Presentation policy: evaluation-ancillary-v1; no rendering or image inspection.

| Item | Requirement | Status | Cell indices | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Assumptions, metric and proximal update inspected; math delimiters checked. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | pending | 1 | Placeholder retained; B5 owns final theorem. |
| 3 | imports | verified | 2,3 | Pinned approved source bootstrap and helper imported in fresh kernel. |
| 4 | function/operator definitions | verified | 5 | Smooth convex f, convex g and h=f+g inspected. |
| 5 | make_ctx_pgm and get_pep_setup | verified | 7 | dense and relaxed proof solves | verified | 11,13,23,25 | Both horizon solves and all owners summarized with actual solver statuses. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 9,10 | Printed N=1..7 values and saved PNG plot output; max discrepancy 4.31910757159315e-09. No visual inspection under evaluation override. |
| 7 | dense and relaxed proof solves | verified | 11,13,23,25 | Both horizon solves and all owners summarized with actual solver statuses. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 13-22,25-33 | Both certificates verified in visible executed cells; candidate formulas remain analytically unverified. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | 34-37 | Same recipe at N=4,6; rank 4 with exclusions (1,1); complete PSD-piece, scalar and offset coverage, residuals below 8e-17. Exact source retained in B3 state. |
| 10 | special-vector identification | verified | 38-47 | Actual 505-candidate scan, sparse-basis search at k=1..4, uniform rank-4 interior basis and endpoint independence checked. |
| 11 | coefficient extraction and closed-form V_k | pending | 48-52 | B4 numerical matrices and full-component reconstructions verified for 0..4; saved-source replay passed. Closed-form coefficients remain B5 work. |
| 12 | symbolic step, base, and boundary identities | pending | 53 | B5. |



