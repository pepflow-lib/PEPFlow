---
name: lyap-closed-form
description: "Derive closed-form Lyapunov coefficients from Block 4 structure, solve symbolic recursions, verify proof identities, and produce a Lyapunov proof notebook. Use when the user asks for /lyap-closed-form, lyap-closed-form, Block 5, closed-form Lyapunov proof, symbolic recursion for V_k, or updating examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb from examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json."
---

# Lyap Closed Form

## Quick Start

Read `references/workflow.md`, then execute it as the authoritative Block 5 workflow.

Start from `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b4.json`, derive unresolved coefficients and local certificate terms from the symbolic recursion, verify the requested identities and boundary normalization, and produce the notebook/proof artifact. Accept a coherent numerical certificate and basis structure even when `lamb_code`, `S_code`, or `coeff_code` is absent; reuse applicable formulas when available.

## Codex Adaptation

- Use SymPy for exact expressions whenever possible; avoid fitting formulas from floats without subsequent symbolic verification.
- Build a minimal one-step symbolic PEPFlow context matching the algorithm's recurrence.
- Verify step, base, and boundary identities in all scalar components (`inner_prod_coords`, `func_coords`, and `offset`), together with sign/domain conditions and the target normalization, before presenting the proof as complete.
- Treat missing coefficient fits as unknown functions to derive in this block. Keep `numerical_certificate_verified`, `analytic_full_pep_verified`, and `lyapunov_proof_verified` separate; numerical agreement or a legacy `proof_valid` flag never establishes an analytic proof.
- Once relevant coefficient definitions exist, the agent may invoke the optional [localize-n-summation-proof](../../optional/localize-n-summation-proof/SKILL.md) skill for a required sign/nonvanishing bottleneck, a proof-critical sum/index identity lacking generic symbolic verification, or a concrete simplification of a complex valid global sign proof. Follow its trigger, skip, and stopping policy within the current task/resource budget; justify necessary signs before proof completion, preserving an existing valid global argument if localization fails.
- Enforce the PEPFlow Lyapunov sign convention: `V_k` should be defined so the proof uses a nonincreasing Lyapunov sequence, i.e. after applying the residual sign convention and nonnegative multipliers the telescoping direction is `V_{k+1} <= V_k` (or the equivalent `V_N <= V_0`). A zero symbolic identity with the opposite inequality direction is not a valid completion.
- Update the notebook under `examples_peppy/{ALGO_NAME}/` and keep durable state under `examples_peppy/{ALGO_NAME}/state/`.
- Place helper verification scripts and other additional files in the notebook's sibling `supplementary/`; use `supplementary/.runtime/` for tool/runtime scratch files, following the [output layout](../../references/output-layout.md).
- For separately created or reused proof-verification files, keep the proof-critical identity definitions, executable checks/results, and sign reasoning in the notebook under the [shared rule](../../references/output-layout.md#proof-verification-files-during-notebook-authoring). Reuse existing cells; elementary domain facts need no dedicated checks.
- Preserve an explicit `require_analytic_full_pep` objective: a completed local Lyapunov proof does not establish a still-unverified global analytic proof.
- If the closed form does not simplify cleanly, report the exact obstruction and the last verified identity.

## Related Skills

This is the final block after `lyap-vectors`.
