---
name: lyap-vectors
description: "Identify special vectors spanning Lyapunov partial sums and extract coefficient patterns as functions of k. Use when the user asks for /lyap-vectors, lyap-vectors, Block 4, special Lyapunov vectors, low-rank decomposition of V_k, coefficient pattern extraction, or generating examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json from examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json."
---

# Lyap Vectors

## Quick Start

Read `references/workflow.md`, then execute it as the authoritative Block 4 workflow.

Start from `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json`, rebuild the partial sums using the stored grouping code, and write `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json`.

## Codex Adaptation

- Reconstruct `lyap` before searching for vectors; do not infer coefficients from stale printed output.
- Build candidate vectors from tagged iterates, gradients or operator outputs, basis vectors, and meaningful differences.
- Use PEPFlow Lyapunov utilities where available instead of reimplementing linear algebra.
- Track both the rank profile and the chosen basis templates in the output state.
- Keep workflow artifacts under `examples_peppy/{ALGO_NAME}/state/`.
- When several decompositions are possible, prefer sparse, interpretable vectors that match the algorithm recurrence.
- In the notebook, use the standard Block 4 section order: `## Identify the vectors composing the Lyapunov function`, `### Candidate-vector scan`, `### Selected basis pattern`, `### Coefficient matrices`, and `### Block 4 conclusion`.

## Related Skills

Run `lyap-closed-form` next to solve the symbolic recursion.
