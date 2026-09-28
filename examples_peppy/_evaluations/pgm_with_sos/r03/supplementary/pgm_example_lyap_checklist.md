# Notebook evidence checklist

Notebook: pgm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 523be8b3a844a1fc2300ceb432078789df101c3018ced33a15be55a03b5656cf
Presentation: evaluation-ancillary-v1; source/output inspection only; no rendered/image inspection.
Static: supplementary/b5-static-002.json (passed). Execution: supplementary/b5-nbconvert-001.log (nbconvert exit 0, fresh attempt kernel).

| Item | Requirement | Status | Zero-based cells | Evidence |
|---|---|---|---|---|
| 1 | title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Algorithm, assumptions and update equations source-inspected. |
| 2 | proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1-3 | Self-contained theorem, piecewise potential, all residual/square terms and telescoping proof appear near the top. |
| 3 | imports | verified | 4-6 | Executed imports use own helpers and frozen approved source. |
| 4 | function/operator definitions | verified | 7 | Executed f,g and parameter definitions. |
| 5 | make_ctx_pgm and get_pep_setup | verified | 8 | Actual algorithm context and PEP setup code executed. |
| 6 | numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 9-11 | Seven optimal solves and rate comparison; saved PNG output present (not viewed). |
| 7 | dense and relaxed proof solves | verified | 12-13 | Dense and sparse solve evidence includes coherent owners and labeled slack matrices. |
| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 14-19 | Initial closed-form search retained; numerical lambda/S coordinate checks and decomposition replayed. Global analytic full-PEP status remains false. |
| 9 | partial-sum Lyapunov construction and rank profile | verified | 20-25 | Explicit partial-sum construction and transported decomposition; rank4 interior at N4,N6, fixed exclusions(1,1), all-index coverage. |
| 10 | special-vector identification | verified | 26-34 | Actual sparse basis search plus candidate scan; adopted basis and every-index endpoint reconstruction executed. |
| 11 | coefficient extraction and closed-form V_k | verified | 35-46 | 55 exact scalar equations for 24 unknowns; three constant freedoms fixed by base normalization. Exact matrix and function-gap formulas compared at every selected index with labeled displays; closed-form potential stated. |
| 12 | symbolic step, base, and boundary identities | verified | 47-60 | Separate symbolic step/base/boundary/N1 calculations visibly build LHS,RHS,diff. Executed Gram/function/offset residuals all zero. Sign/domain and radius normalization arguments inspected. |
