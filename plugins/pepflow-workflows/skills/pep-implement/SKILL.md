---
name: pep-implement
description: "Create or validate a PEPFlow algorithm setup module, initialize the Lyapunov notebook, and run initial numerical convergence checks. Use when the user asks for /pep-implement, pep-implement, Block 1, implementing a new PEPFlow example, creating examples_peppy/{ALGO_NAME}/{ALGO_NAME}_setup.py, or turning an algorithm description into a PEPFlow setup plus examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json state."
---

# PEP Implement

## Quick Start

Read `references/workflow.md`, then execute it as the authoritative Block 1 workflow.

Use the workflow's `$ARGUMENTS` placeholder as the user's algorithm description. When the workflow says "print", summarize the result to the user in normal Codex prose. When it says "create", edit files directly in the repository.

## Codex Adaptation

- Use the repository root from the current workspace unless `git rev-parse --show-toplevel` proves otherwise.
- Use `.venv/bin/python3` for Python calls when it exists; otherwise inspect the project and choose the local Python path conservatively.
- Prefer reading existing examples under `examples_peppy/` before creating new setup modules.
- Preserve the state-file contract: write `examples_peppy/{ALGO_NAME}/state/{ALGO_NAME}_b1.json` with the fields expected by later skills.
- Initialize `examples_peppy/{ALGO_NAME}/{ALGO_NAME}_example_lyap.ipynb` as described in the workflow, including the Block 1 numerical-evidence plot.
- Avoid system-level temporary directories; use `examples_peppy/{ALGO_NAME}/state/` for workflow artifacts and `examples_peppy/{ALGO_NAME}/state/.runtime/` only for tool/runtime scratch files when needed.
- Verify with `python -m pepflow.pep_runner` or the command specified in the workflow, then report whether the observed rates match the conjecture.
- If an existing setup module is present, read it first and patch only what is needed.

## Related Skills

Continue with `pep-full-proof` for Block 2, or use `pep-analyze` when the user wants the complete end-to-end workflow.
