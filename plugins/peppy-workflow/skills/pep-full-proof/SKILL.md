---
name: pep-full-proof
description: "Find tight PEPFlow performance guarantees with explicit full-PEP dual certificates, sparse lambda structure, S matrices, and numerical or analytic proof state for Lyapunov discovery. Use when the user asks for /pep-full-proof, pep-full-proof, Block 2, full PEP proof, sparse dual certificates, or generating examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json from examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json."
---

# PEP Full Proof

## Quick Start

Read `references/workflow.md`, then execute it as the authoritative Block 2 workflow.

Use the algorithm name from the user request or from `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json`. Keep the dense solve, sparsity search, selected-certificate checks, and initial closed-form search. Reuse applicable established formulas; otherwise make a meaningful initial attempt, record unresolved components, and continue numerically when the certificate is valid. Missing closed forms alone do not require a user checkpoint. Preserve an explicitly requested analytic full-PEP proof as an unresolved objective until it is established.

## Codex Adaptation

- Load `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json` first and confirm `algo_name`, `obj_tag`, `params_json`, `N_verify`, and `conjectured_rate`. On a Block 3 return, obtain that requested horizon's own coherent certificate, preserve prior samples in `supplementary/`, and update the selected handoff together. Reuse applicable initial-search records or formulas without requiring a new full closed-form search merely because N changed.
- Use `.venv/bin/python3` for Python calls when available.
- When displaying matrices, summarize the nonzero or structurally important entries instead of dumping huge tables unless the user asks for full output.
- In proof notebooks, use `pf.pprint_labeled_matrix(...)` for proof-bearing matrices such as candidate lambda formulas, S candidates/decompositions, Lyapunov coefficient matrices, and proof residuals; summarize raw dense/relaxed certificate matrices unless full tables are requested.
- Store durable output in `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json`; preserve legacy display keys and add the coherent numerical certificate, provenance, checks, decomposition, and initial-search record specified by the workflow. Allow absent or null `lamb_code`/`S_code` instead of zero placeholders.
- Keep `numerical_certificate_verified`, `analytic_full_pep_verified`, and `lyapunov_proof_verified` separate. Numerical agreement and legacy `proof_valid` do not establish an analytic proof. Capture every scalar/matrix dual and S from one solve; never combine saved lambda with a newly solved S or extras.
- Once relevant candidate definitions exist, the agent may invoke the optional [localize-n-summation-proof](../../optional/localize-n-summation-proof/SKILL.md) skill for a required sign/nonvanishing bottleneck, a proof-critical sum/index identity lacking generic symbolic verification, or a concrete simplification of a complex valid global sign proof. Follow its trigger, skip, and stopping policy within the current task/resource budget; unresolved localization does not block a valid numerical handoff.
- Keep required dense/relaxed solver results in the notebook's sibling `state/`; place exploratory JSON, debug dumps, helper scripts, and other additional files in `supplementary/`, following the [output layout](../../references/output-layout.md).
- Treat near-zero dual entries carefully: state the tolerance used and rerun verification after imposing sparsity.
- Before using LDL for the Gram certificate `S`, inspect any existing `examples_peppy/_references/{ALGO_NAME}/` notebook/module for verified `S_guess`, `S_piece`, square-term, or rank-profile constructions; adapt those proof-specific decompositions into `S_code` and, when possible, named pieces for Block 3.
- If the numerical certificate disagrees with the conjecture, pause the proof workflow and diagnose the setup, parameters, and relaxation before proceeding.

## Related Skills

Run `lyap-define` next for Block 3, or use `pep-analyze` for the combined analysis flow.
