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
- Before using a generic LDL decomposition for `S`, inspect any existing `examples_peppy/_references/{ALGO_NAME}/` notebook/module for verified `S_guess`, `S_piece`, square-term, or rank-profile constructions; adapt those proof-specific pieces first, and do not treat missing per-step fields in `{ALGO_NAME}_b2.json` as proof that no known decomposition exists.
- Use the PEPFlow Lyapunov sign convention: define `V_k` so the final proof makes `V_k` nonincreasing (or at least `V_k <= V_0`) under the chosen residual convention. Do not accept a grouping merely because its symbolic residual is zero; also verify the inequality direction used in the telescoping proof.
- Verify the rank profile numerically and state the tolerance.
- In notebooks, the visible partial-sum construction cell should print ranks one per line as `rank V_k: r`, include a blank line after `rank V_0`, then print the interior-rank consistency check in the same cell; do not print every grouped dual term or add a separate rank-profile dump cell by default.
- Keep workflow artifacts under `examples_peppy/{ALGO_NAME}/state/`.
- If ranks are inconsistent, inspect indexing and dual grouping before changing the mathematical ansatz.

## Related Skills

Run `lyap-vectors` next to identify special spanning vectors.
