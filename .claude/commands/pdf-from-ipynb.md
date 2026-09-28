# /pdf-from-ipynb: Optional theorem-and-proof PDF

Use `plugins/peppy-workflow/optional/pdf-from-ipynb/SKILL.md` and its linked `references/workflow.md` to turn an existing Peppy output notebook into a self-contained theorem-and-proof PDF. Deliver the PDF together with the exact `.tex` used to compile it by default, keeping build artifacts under the notebook's `supplementary/` directory.

Treat `$ARGUMENTS` as the notebook path plus any requested output path, title, or language. If omitted, use the final notebook identified in the conversation; ask only if the input remains ambiguous.

This command is optional and is not part of the required five-block analysis flow. Preserve the source notebook and the mathematical status of its claims.
