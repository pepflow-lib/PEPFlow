---
name: lyap-define
description: "Build Lyapunov partial-sum sequences from PEPFlow full-PEP dual certificates and verify their rank profile. Use when the user asks for /lyap-define, lyap-define, Block 3, defining the Lyapunov function, constructing V_k partial sums, or generating examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json from examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json."
---

# Lyap Define

## Quick Start

Read `references/workflow.md`, then execute it as the authoritative Block 3 workflow.

Start from `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json` and preserve the workflow's dual extraction, grouping-code construction, partial-sum verification, and `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b3.json` output.

## Codex Adaptation

- Recreate the PEP context exactly as in the setup module without a new solve, and verify the complete saved Block 2 numerical certificate before evaluating partial sums. If recovery requires solving, replace and recheck every certificate component together in Block 2.
- Keep every function/operator interpolation group and every scalar/PSD named extra from the same certificate until grouping and full-coordinate coverage are verified.
- Require Block 2's recorded initial closed-form attempt, not successful formulas. Null `lamb_code` or `S_code` does not block numerical partial sums or trigger another analytic search here. Keep `numerical_certificate_verified`, `analytic_full_pep_verified`, and `lyapunov_proof_verified` distinct.
- Preserve exact executed certificate-check, decomposition, and grouping source for `lyap-vectors` to replay against the same saved numerical certificate; retain all partial-sum scalar coordinates and unresolved formulas. Keep the actual mathematical checks and grouping visible in the notebook.
- Before using a generic LDL decomposition for `S`, inspect any existing `examples_peppy/_references/{ALGO_NAME}/` notebook/module for verified `S_guess`, `S_piece`, square-term, or rank-profile constructions; adapt those proof-specific pieces first, and do not treat missing per-step fields in `{ALGO_NAME}_b2.json` as proof that no known decomposition exists. Otherwise numerical reverse LDL is allowed under the workflow's applicability and reconstruction checks, without a closed-form requirement.
- Use the PEPFlow Lyapunov sign convention: define `V_k` so the final proof makes `V_k` nonincreasing (or at least `V_k <= V_0`) under the chosen residual convention. Do not accept a grouping merely because its symbolic residual is zero; also verify the inequality direction used in the telescoping proof.
- Confirm the same interior rank at two or more distinct horizons with fixed boundary exclusions of at most two indices at each end, including V_0/V_N, and at least three retained indices per horizon. State the tolerance/scaling convention; equal rank does not establish a shared basis.
- In notebooks, the visible partial-sum construction cell should print ranks one per line as `rank V_k: r`, include a blank line after `rank V_0`, then print the interior-rank consistency check in the same cell; do not print every grouped dual term or add a separate rank-profile dump cell by default.
- Keep required main-step state in the notebook's sibling `state/`; place helper modules and other additional files in `supplementary/`, following the [output layout](../../references/output-layout.md).
- If the pattern is unhelpful, inspect indexing and rank credibility, vary grouping/SOS assignment and verified decompositions of the same S, then increase N within the same attempt, normally 4, 6, 8, 10, 12. Do not stop merely after a few reorderings. Obtain a complete matching Block 2 certificate at each new horizon, keep the existing time budget, and require explicit user authorization before any N > 12.
- Keep multi-horizon evidence in supplementary/ and save a concise rank_search summary with the selected certificate in Block 3 state. Block 3 checks rank and coverage; basis reconstruction remains in Block 4 and the arbitrary-horizon analytic proof remains in Block 5.

## Related Skills

Run `lyap-vectors` after the rank/coverage checks pass to identify special spanning vectors.
