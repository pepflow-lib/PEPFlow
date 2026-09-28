---
name: lyap-vectors
description: "Identify special vectors spanning Lyapunov partial sums, verify numerical coefficient reconstructions, and optionally fit coefficient patterns before analytic derivation. Use when the user asks for /lyap-vectors, lyap-vectors, Block 4, special Lyapunov vectors, low-rank decomposition of V_k, coefficient pattern extraction, or generating examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json from examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json."
---

# Lyap Vectors

## Quick Start

Read `references/workflow.md`, then execute it as the authoritative Block 4 workflow.

Start from `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json`, rebuild the partial sums using the stored grouping code, and write `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json`.

## Codex Adaptation

- Reconstruct `lyap` from the selected coherent B3 certificate before searching for vectors; consume its `rank_search` evidence and fixed boundary exclusions, retaining the legacy one-index-per-end convention when that record is absent. Do not infer coefficients from stale printed output.
- Build candidate vectors from tagged iterates, gradients or operator outputs, basis vectors, and meaningful differences.
- Use PEPFlow Lyapunov utilities where available instead of reimplementing linear algebra.
- Track the rank profile, chosen basis templates, numerical coefficient matrices, and all function-value/constant and exceptional-case terms, including documented exceptions at up to two indices at each end. Require successful independence and reconstruction checks for every index. If basis discovery fails, return to Block 3's authorized recovery within the same attempt; do not proceed to coefficient extraction without a consistent basis.
- Coefficient fitting is optional. Pass null `coeff_code` and explicit unknown coefficient functions to Block 5 when formulas are unresolved; do not stop solely to request a pattern. Keep numerical-certificate, analytic full-PEP, and analytic Lyapunov verification statuses separate.
- Keep required main-step state in the notebook's sibling `state/`; place candidate-search scripts, exploratory output, and other additional files in `supplementary/`, following the [output layout](../../references/output-layout.md).
- When several decompositions are possible, prefer sparse, interpretable vectors that match the algorithm recurrence.
- In the notebook, use the standard Block 4 section order: `## Identify the vectors composing the Lyapunov function`, `### Candidate-vector scan`, `### Selected basis pattern`, `### Coefficient matrices`, and `### Block 4 conclusion`.

## Related Skills

Run `lyap-closed-form` next to solve the symbolic recursion.
