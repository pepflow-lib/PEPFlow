# Notebook evidence checklist

Notebook: pgm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: fa7567f923381498cca00cd963c2ef0d2fa219b5b010fe11a9a0b34a3de70089
Presentation: evaluation-ancillary-v1; source math checks passed; rendered inspection omitted by override.

| Item | Requirement | Status | Cells (zero-based) | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Algorithm, assumptions and updates present in source. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1-3 | Separate Proof Statement, Theorem and Proof outline; full finite-product potential, every residual and square, base, terminal, N=1 and signs. |
| 3 | imports | verified | 4-5 | Approved-only imports and private execution bootstrap; fresh kernel passed. |
| 4 | function/operator definitions | verified | 6 | Composite f+g, smoothness L and proximal g are explicit. |
| 5 | make_ctx_pgm and get_pep_setup | verified | 7 | Actual recursion, composite stationarity, initial squared-distance bound and objective gap. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 8-9 | Executed N=1..7 values and comparison PNG retained; source and data checked, no image inspection under override. |
| 7 | dense and relaxed proof solves | verified | 10-12 | Dense and sparse solves with default/fallback provenance, nonoptimal statuses retained, objective agreement checked. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 13-16 | Initial analytic candidate attempt, coherent lambda/S complete coordinate check, cones and reverse LDL reconstruction; global analytic proof remains separately unverified. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | 17-22 | Actual partial_sum and lyap construction, complete coordinate coverage, same-S square assignment, ranks 5 across N=4,6 and fixed exclusions (1,1). |
| 10 | special-vector identification | verified | 23-34 | Visible candidate scan, sparse basis search, independence, labeled coefficient matrices and every-index full-coordinate reconstruction. |
| 11 | coefficient extraction and closed-form V_k | verified | 33-40 | Symbolic Schur equations and transfer-product solution with terminal condition; labeled closed/decomposed coefficients; all-coordinate comparison max below 3.2e-6; full formula and function terms near top and after derivation. |
| 12 | symbolic step, base, and boundary identities | verified | {'step': 43, 'base': 46, 'boundary': 49, 'small': 52} | Separate symbolic PEPFlow contexts and visible LHS/RHS/diff, labeled Gram zero matrices, function and offset zeros; N=1 exact check; positive transfer-matrix audit and all sign/domain/normalization arguments. |
