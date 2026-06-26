---
name: lyap-define
description: "Build Lyapunov partial-sum sequences from PEPFlow full-PEP dual certificates and verify their rank profile. Use when the user asks for /lyap-define, lyap-define, Block 3, defining the Lyapunov function, constructing V_k partial sums, or generating examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json from examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json."
---

# Lyap Define

## Quick Start

Read `references/workflow.md`, then execute it as the authoritative Block 3 workflow.

Start from `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json` and preserve the workflow's dual extraction, grouping-code construction, partial-sum verification, and `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json` output.

## Codex Adaptation

- Recreate the PEP context exactly as in the setup module before evaluating expressions.
- Keep interpolation duals and extra named duals separate until the grouping is verified.
- Prefer small, inspectable grouping code that can be stored in JSON and re-executed by `lyap-vectors`.
- Verify the rank profile numerically and state the tolerance.
- In notebooks, the visible partial-sum construction cell should print ranks one per line as `rank V_k: r`, include a blank line after `rank V_0`, then print the interior-rank consistency check in the same cell; do not print every grouped dual term or add a separate rank-profile dump cell by default.
- Keep workflow artifacts under `examples_peppy/{ALGO_NAME}/state/`.
- If ranks are inconsistent, inspect indexing and dual grouping before changing the mathematical ansatz.

## Related Skills

Run `lyap-vectors` next to identify special spanning vectors.
