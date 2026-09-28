---
name: lean-from-ipynb
description: "Formalize a selected theorem or proof from a Peppy/PEPFlow output Jupyter notebook in Lean, with a final-theorem entry usable in VS Code and the CLI, a pinned Lake project, and itemized token usage. Use when the user explicitly requests this optional Lean step or invokes lean-from-ipynb; ordinary analysis and PDF export do not require it."
---

# Lean from IPYNB

Turn the proof presented in an existing output notebook into Lean definitions, supporting lemmas, and the selected final theorem. This is an optional formalization step, not a sixth required analysis block. Keep Lean separate from PEPFlow's Python dependencies.

## Invocation

Accept a notebook path and an optional target theorem, lemma, or proof scope. For example:

```text
$lean-from-ipynb examples_peppy/my_algorithm/my_algorithm.ipynb
$lean-from-ipynb examples_peppy/my_algorithm/my_algorithm.ipynb --target "coefficient positivity"
```

These are natural-language skill arguments, not an installed command-line parser. By default, formalize the notebook's principal final theorem and the supporting results needed for it. Honor a request for only a particular positivity lemma or final implication.

If no path is given, use the notebook identified in the conversation. Resolve relative paths from the invocation directory before changing directories. Accept an omitted `.ipynb` extension when it resolves uniquely; for a directory input, select its unambiguous main notebook. Check literal paths first and resolve pasted Markdown escapes or duplicate path segments only against existing candidates. Ask only when the notebook or intended claim remains ambiguous; do not select the most recently modified experiment as a substitute.

Read the shared [output layout](../../references/output-layout.md) and [workflow](references/workflow.md), including its token-accounting section, before substantive formalization. For this optional task, the Lean-specific layout below governs the final entry, Lake configuration, and `lean/` artifacts where the shared layout otherwise places auxiliary files in `supplementary/`.

## Essential boundaries

- Preserve the source notebook, setup, and state. Read notebook JSON and its referenced proof files without executing the analysis by default. Do not restart PEP searches or Blocks 1-5 to perform this optional task.
- Preserve the intended statement, coefficient definitions, algorithm, parameter domains, and quantifiers. Formalize necessary supporting lemmas; never silently turn an unproved required result into an assumption of the final theorem.
- Distinguish a local lemma, a final implication under explicit intermediate assumptions, and an end-to-end theorem from the original function and algorithm assumptions. Report the scope actually checked.
- Source generation, `#check`, numerical tests, and solver or SymPy success flags do not establish the requested Lean theorem. Build the proof library and check the exact delivered entry file, including its axiom dependencies.
- The final entry must be inside a discoverable Lake project: place `lakefile.toml` or `lakefile.lean` and a pinned `lean-toolchain` in its directory or an ancestor, never only in a child directory. Resolve supporting imports through Lake and use the same toolchain for the CLI and language server.
- Verify the exact delivered entry through both the CLI and `lake serve`; require completed document processing, not just an empty early diagnostic list. Report each check separately, including any check that could not run. A CLI pass alone does not establish editor support.
- Use available task-level usage counters. Report unavailable or partially observed token usage honestly; lack of telemetry does not prevent completing the mathematical work.

## Deliverables

Let `NOTEBOOK_DIR` be the resolved notebook parent and `STEM` its filename without `.ipynb`. Use this default layout, honoring an explicit user override:

```text
NOTEBOOK_DIR/
  STEM.ipynb
  STEM_lean.lean                 # selected final theorem(s), check commands
  lakefile.toml                  # or lakefile.lean; project covers the entry
  lean-toolchain                 # pinned version used by CLI and VS Code
  lean/
    lake-manifest.json
    NotebookProofs.lean         # library name may follow the existing project
    NotebookProofs/             # definitions and proofs, as needed
    STEM_verification.md        # scope, reproduction, results, token breakdown
    .lake/                      # local dependencies and build cache
```

`lean/` is the work folder beside the original notebook, not a repository-root or supplementary folder. The Lake project normally starts at `NOTEBOOK_DIR`, with its proof library's source directory set to `lean/`. For a completed formalization, the sibling `STEM_lean.lean` must expose named theorems with the complete statements the user wants to check; it is not just an import or a list of `#check` commands. Keep proof implementation and auxiliary artifacts inside `lean/`, with the discoverable project configuration beside the entry or in an existing ancestor project.

Reuse an existing compatible project and separate notebooks by module namespace and stem-specific entry/report names. Inspect existing files before editing; do not reinitialize a project or overwrite an unrelated proof. An existing child `lean/` project can remain a local dependency of a thin parent project covering the entry; see the workflow. Align their toolchain pins and do not change mathematical statements or proofs to repair project discovery. Resolve incompatible toolchains without silently moving the requested outputs.

Report the entry file, discoverable project root, target theorem names, proof scope/status, CLI and language-server results, exact check commands, and itemized token usage. Include any incomplete proof or unperformed check. No PDF, extra notebook, or core dependency change is part of this skill.
