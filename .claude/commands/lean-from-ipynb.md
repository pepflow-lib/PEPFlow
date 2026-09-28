# /lean-from-ipynb: Optional Lean proof from a notebook

Use `plugins/peppy-workflow/optional/lean-from-ipynb/SKILL.md` and its linked `references/workflow.md` to formalize the selected proof from an existing Peppy notebook.

Treat `$ARGUMENTS` as the notebook path plus any requested theorem, lemma, or proof scope. If omitted, use the notebook identified in the conversation; ask only if the source or target remains ambiguous. A uniquely resolvable notebook stem without `.ipynb` is accepted.

Create or reuse `lean/` beside the notebook for supporting proofs and working artifacts. Put `lakefile.toml` or `lakefile.lean` and a pinned `lean-toolchain` beside the final entry or in a compatible ancestor, so it belongs to a discoverable Lake project. Deliver `<notebook-stem>_lean.lean` beside the notebook as the exact final-theorem check target. Build the library and entry, verify that exact file through both the CLI and Lean language server with the same pinned toolchain, and report proof scope, axiom dependencies, both verification outcomes, reproduction commands, and itemized task-token usage. Explicitly identify checks that could not run. Preserve mathematical statements and proofs when repairing project configuration. Mark unavailable token counts honestly.

This command is optional. Preserve the source notebook, setup, and state; do not restart Blocks 1-5, add Lean to PEPFlow's Python dependencies, or silently weaken the requested statement.
