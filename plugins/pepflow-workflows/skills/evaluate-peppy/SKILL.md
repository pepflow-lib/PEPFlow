---
name: evaluate-peppy
description: "Run the optional Peppy five-example reproducibility evaluation when explicitly requested, recording selected conditions and configurable attempts (default five for the full suite), PGM with and without supplied SOS, block-level costs, and final Lyapunov proof validity. Not part of ordinary analysis or pytest."
---

# Evaluate Peppy

Read and follow the [canonical optional skill](../../optional/evaluate-peppy/SKILL.md). It owns the execution protocol, case inputs, clean-room policy and evaluator rubric.

Treat the user's arguments as model/inference settings, `conditions=<condition_id,...>`, `repetitions=<positive integer>` or a natural-language repetition count, and any explicit campaign overrides. Apply the canonical defaults when omitted, including all six conditions and five repetitions per condition, except an explicit single-condition timing request defaults to one repetition. Use the requested subset without adding attempts; resolve missing model settings and invalid or ambiguous selections/counts under the canonical rules. Follow campaign protocol `2026-09-20.isolation-recovery-v1`, including its evaluation-only rendering override, while preserving the frozen mathematical workflow. This entry registers the optional command and does not introduce a sixth analysis block. Do not launch experiments merely because this skill is being edited or discussed.
