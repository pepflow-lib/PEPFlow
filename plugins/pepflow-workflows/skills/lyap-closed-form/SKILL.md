---
name: lyap-closed-form
description: "Derive closed-form Lyapunov coefficients from Block 4 structure, solve symbolic recursions, verify proof identities, and produce a Lyapunov proof notebook. Use when the user asks for /lyap-closed-form, lyap-closed-form, Block 5, closed-form Lyapunov proof, symbolic recursion for V_k, or updating examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb from examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json."
---

# Lyap Closed Form

## Quick Start

Read `references/workflow.md`, then execute it as the authoritative Block 5 workflow.

Start from `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json`, solve the symbolic recursion, verify the identities requested by the workflow, and produce the notebook/proof artifact.

## Codex Adaptation

- Use SymPy for exact expressions whenever possible; avoid fitting formulas from floats without subsequent symbolic verification.
- Build a minimal one-step symbolic PEPFlow context matching the algorithm's recurrence.
- Verify all three symbolic identities described in the workflow before presenting the proof as complete.
- Enforce the PEPFlow Lyapunov sign convention: `V_k` should be defined so the proof uses a nonincreasing Lyapunov sequence, i.e. after applying the residual sign convention and nonnegative multipliers the telescoping direction is `V_{k+1} <= V_k` (or the equivalent `V_N <= V_0`). A zero symbolic identity with the opposite inequality direction is not a valid completion.
- Update the notebook under `examples_peppy/{ALGO_NAME}/` and keep durable state under `examples_peppy/{ALGO_NAME}/state/`.
- Avoid system-level temporary directories; use `examples_peppy/{ALGO_NAME}/state/.runtime/` only for tool/runtime scratch files when needed.
- If the closed form does not simplify cleanly, report the exact obstruction and the last verified identity.

## Related Skills

This is the final block after `lyap-vectors`.
