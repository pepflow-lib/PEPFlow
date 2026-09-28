Notebook: ogm_example_lyap.ipynb
Last reviewed block: B5
SHA-256: 44c6101dac16b24fc626700355df543b3bc98669ba6a94ddc79ecf1f6cf9ac5e
Presentation policy: evaluation-ancillary-v1. Rendered/image inspection intentionally omitted; source delimiter/control-character checks passed. No rendered verification is claimed.

| Item | Status | Cells | Evidence |
|---|---|---|---|
| 1. title, problem description, and the algorithm update equations in LaTeX | verified | 0 | Complete supplied assumptions and update equations, including special terminal theta recurrence, in source. |
| 2. proof statement placeholder, to be filled with the final theorem and proof outline in Block 5 | verified | 1–3 | Separate theorem and self-contained proof outline state all-index potential and exact rate, local residual identities, signs, N1 and full-PEP telescoping. |
| 3. imports | verified | 4–6 | Approved-source/private-helper paths and runtime settings visible; kernel executed imports. |
| 4. function/operator definitions | verified | 7 | L,R and smooth-convex function definitions executed. |
| 5. make_ctx_ogm and get_pep_setup | verified | 8 | Full context builder and PEP definition visible, with correct radius squared and terminal gradient. |
| 6. numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate | verified | 9–10 | N1–N7 printed values plus embedded PNG plot; max candidate discrepancy 3.12e-9. Plot presence checked without inspecting image. |
| 7. dense and relaxed proof solves | verified | 11–15 | Dense solve, threshold trial and selected chain solve preserved in state/supplementary; complete selected inventory, solver settings and gap 3.16e-9 shown. |
| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 16–23, 45–63 | Labeled candidates and direct S reconstruction; complete numerical identity with max residual 1.39e-9; exact local identities and telescoping prove global formulas. Historical numerical statuses distinguished from final analytic status. |
| 9. partial-sum Lyapunov construction and rank profile | verified | 24–30 | Visible partial_sum loop and exact saved-source replay; rank 3 confirmed at N4,N6 with exclusions(1,1); full coverage max 5.63e-9. |
| 10. special-vector identification | verified | 31–39 | Actual deduplicated scan, column-space filtering and sparse basis search outputs for all nonzero k; independence including endpoints. |
| 11. coefficient extraction and closed-form V_k | verified | 40–44, 45–63 | Labeled numeric and candidate C matrices; function and offset components included; all-index full reconstruction max 3.05e-10; exact closed-form expression proved below. |
| 12. symbolic step, base, and boundary identities | verified | 47–63 | Five exact checks show labeled Gram and function zero matrices and zero constants: interior49, base52, terminal55, N1 58, normalization61; sign/domain argument62–63. |