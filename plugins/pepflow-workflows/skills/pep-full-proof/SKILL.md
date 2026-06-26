---
name: pep-full-proof
description: "Find tight PEPFlow performance guarantees with explicit full-PEP dual certificates, sparse lambda structure, S matrices, and algebraic proof state. Use when the user asks for /pep-full-proof, pep-full-proof, Block 2, full PEP proof, sparse dual certificates, or generating examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json from examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json."
---

# PEP Full Proof

## Quick Start

Read `references/workflow.md`, then execute it as the authoritative Block 2 workflow.

Use the algorithm name from the user request or from `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json`. Keep the workflow's dense solve, sparsity detection, relaxed solve, and symbolic verification phases intact.

## Codex Adaptation

- Load `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json` first and confirm `algo_name`, `obj_tag`, `params_json`, `N_verify`, and `conjectured_rate`.
- Use `.venv/bin/python3` for Python calls when available.
- When displaying matrices, summarize the nonzero or structurally important entries instead of dumping huge tables unless the user asks for full output.
- In proof notebooks, use `pf.pprint_labeled_matrix(...)` for proof-bearing matrices such as candidate lambda formulas, S candidates/decompositions, Lyapunov coefficient matrices, and proof residuals; summarize raw dense/relaxed certificate matrices unless full tables are requested.
- Store durable output in `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b2.json`; later Lyapunov skills depend on the same keys.
- Avoid system-level temporary directories; store dense/relaxed solver outputs and scratch JSON under `examples_peppy/{ALGO_NAME}/state/`.
- Treat near-zero dual entries carefully: state the tolerance used and rerun verification after imposing sparsity.
- Before using LDL for the Gram certificate `S`, inspect any existing `examples_peppy/_references/{ALGO_NAME}/` notebook/module for verified `S_guess`, `S_piece`, square-term, or rank-profile constructions; adapt those proof-specific decompositions into `S_code` and, when possible, named pieces for Block 3.
- If the numerical certificate disagrees with the conjecture, pause the proof workflow and diagnose the setup, parameters, and relaxation before proceeding.

## Related Skills

Run `lyap-define` next for Block 3, or use `pep-analyze` for the combined analysis flow.
