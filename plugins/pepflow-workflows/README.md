# Peppy workflow instructions

This plugin provides the five stages described in the Peppy paper:

1. [pep-implement](skills/pep-implement/SKILL.md): encode the algorithm and construct its PEP.
2. [pep-full-proof](skills/pep-full-proof/SKILL.md): obtain and examine a numerical certificate.
3. [lyap-define](skills/lyap-define/SKILL.md): construct Lyapunov partial sums.
4. [lyap-vectors](skills/lyap-vectors/SKILL.md): find an interpretable basis and reconstruct coefficients.
5. [lyap-closed-form](skills/lyap-closed-form/SKILL.md): complete and check the analytic proof.

The [evaluation procedure](optional/evaluate-peppy/SKILL.md) coordinates fresh generation and independent review. Those runs use a coding-agent host and may incur substantial model usage. They are separate from the [saved experimental results and reproduction tools](../../examples_peppy/_evaluations/README.md).

For historical reproduction, use the frozen framework snapshot and environment identified in the experiment guide. The current plugin can differ from the campaign-time instructions. The plugin shares the repository's [Apache-2.0 license](../../LICENSE).
