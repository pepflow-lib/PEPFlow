---
name: lean-from-ipynb
description: "Formalize a selected Peppy/PEPFlow notebook proof in Lean with a pinned Lake project, final-theorem entry usable in VS Code and the CLI, and task-token report. Optional: use when the user explicitly requests Lean formalization or invokes lean-from-ipynb, not during ordinary analysis or PDF export."
---

# Lean from IPYNB

Read [the optional skill instructions](../../optional/lean-from-ipynb/SKILL.md), then follow their linked workflow. Keep supporting proofs in the notebook's `lean/` directory and the final check target in the sibling `<notebook-stem>_lean.lean` file. Put the Lake configuration and pinned `lean-toolchain` beside that entry or in a compatible ancestor project so VS Code discovers it. Verify the exact entry through both the CLI and Lean language server, using the same toolchain, and report any check that could not run. Report token usage by task with honest measurement coverage.

This entry registers the optional skill. Its canonical instructions live under `optional/lean-from-ipynb/`; invocation is not required to complete any analysis block.
