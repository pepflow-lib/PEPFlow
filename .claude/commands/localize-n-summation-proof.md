# /localize-n-summation-proof: Optional local N-summation proof

Read and follow [the canonical optional skill](../../plugins/peppy-workflow/optional/localize-n-summation-proof/SKILL.md) for an existing Peppy notebook. Treat `$ARGUMENTS` as the notebook path plus an optional target coefficient or proof obligation; use the current notebook when unambiguous.

This command supports explicit requests and agent-selected invocation within the current proof task when a required sign or generic symbolic verification is a bottleneck, or a concrete local reduction would materially simplify a complex valid global proof. Skip elementary or already concise arguments and honor a user opt-out. Apply the canonical scope and stopping conditions without requiring a separate skill request.

Keep the proof-critical argument and exact generic-index checks in the same notebook. Preserve the selected theorem and coefficients, an existing valid global proof if localization fails, and the numerical handoff between main blocks. This optional procedure does not create a sixth block, extra reports, or PDF/TeX exports.
