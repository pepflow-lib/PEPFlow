# Formalize an existing notebook proof in Lean

## 1. Establish the target and accounting boundary

Resolve notebook and output paths as specified by the skill. Start the usage record before reading the proof, using the accounting rules below. Record the target and scope in `lean/<stem>_verification.md`; do not create a separate planning report.

Read the notebook's Markdown, code, saved outputs, and explicitly referenced local proof files. Locate the theorem, proof outline, final coefficients, Lyapunov expression, step/base/boundary identities, and supporting sign arguments. A `b5.json` file is not required. Cached output and execution counts do not certify freshness; compare the mathematical expressions with the claimed theorem.

Map the statement to source sections or cell IDs (otherwise 1-based cell positions) and referenced definitions. State the function/operator class, comparison solution, update rule, metric, parameter/index domains, recurrence and initial data, denominator conditions, and small-horizon cases.

| Scope | Required connection |
| --- | --- |
| Selected lemma | Original coefficient/sequence/matrix definitions and domain imply the selected claim. |
| Final implication | Explicitly listed intermediate hypotheses imply the final bound; these hypotheses are not reported as proved. |
| End-to-end theorem | Original function and algorithm assumptions imply the supporting inequalities, identities, and final bound. |

Without a narrower request, target the principal final theorem. Do not downgrade an end-to-end request to a certificate implication without saying what remains unproved. Supply ordinary missing proof steps and supporting lemmas. If a mathematical gap cannot be closed, record it precisely and retain useful partial results; do not change the requested rate, domain, or theorem to obtain a passing build.

## 2. Prepare a discoverable, pinned Lake project

Inspect available `lean`, `lake`, and `elan` commands, configuration in the entry's directory and ancestors, and any existing `NOTEBOOK_DIR/lean` project. Set `PROJECT_ROOT` to the Lake project that will cover the exact delivered entry. The entry must be under this root, with `lakefile.toml` or `lakefile.lean` and a pinned `lean-toolchain` at that root. A child-only `lean/` configuration cannot serve a sibling entry: VS Code searches ancestors, not child directories.

For a new project, place the Lake configuration and `lean-toolchain` in `NOTEBOOK_DIR`; keep the proof library and working artifacts in `lean/`. A TOML configuration for an ordinary module-compatible stem is:

```toml
name = "notebook_proofs"
version = "0.1.0"
defaultTargets = ["NotebookEntry"]
packagesDir = "lean/.lake/packages"
buildDir = "lean/.lake/build"
manifestFile = "lean/lake-manifest.json"

[[lean_lib]]
name = "NotebookProofs"
srcDir = "lean"

[[lean_lib]]
name = "NotebookEntry"
roots = ["<stem>_lean"]
```

Substitute the actual entry module name and add only required dependencies, pinning mathlib to a revision compatible with the exact Lean version in `lean-toolchain`. Resolve and retain the manifest before building. Confirm configuration fields against the pinned Lake version; when an existing project uses a different supported artifact layout, preserve it. Keep downloaded toolchains, dependencies, and build caches ignored, not delivered as source changes. Do not initialize a nested Git repository merely to initialize Lake.

Reuse compatible existing configuration rather than overwrite it. If a child `lean/` project already contains the library, keep it intact and create or extend a thin project at `NOTEBOOK_DIR` (or a compatible existing ancestor). Declare the child package as a local path dependency, using its actual package name:

```toml
[[require]]
name = "notebook_proofs"
path = "lean"
```

In that parent, use a distinct package name, the `NotebookEntry` target above, the same `lean-toolchain` pin as the child, and separate build/manifest paths such as `lean/.lake/editor-build` and `lean/editor-lake-manifest.json`. Omit the duplicate `NotebookProofs` library declaration: the child dependency provides it. Share the existing dependency cache where compatible, resolve the parent manifest, and check both pins agree. Do not move or change mathematical statements or proofs to fix discovery. Preserve existing targets and use stem-specific entry targets when multiple notebooks share a project.

Use valid Lean names for supporting modules independently of the notebook filename. Preserve `<stem>_lean.lean` and quote file paths. If its stem needs special module-name handling, configure a supported escaped root or explicit Lake check target for that exact file; do not silently rename it or verify a surrogate. Confirm the nearest configuration and toolchain seen from the entry's directory select `PROJECT_ROOT`; nested pins or Lake files must not redirect editor discovery to a different project.

Install or reuse the pinned toolchain through the available Lean manager, so VS Code and terminal invocations can both find it. If using an existing local toolchain, register it under the matching pin where supported. A private shell PATH change or `LEAN_PATH` that only makes the CLI work is insufficient. Record the resolved `lake` executable and `lake env lean --version` at `PROJECT_ROOT`; verify the server launches that toolchain and check for environment/toolchain overrides. LSP `serverInfo.version` can describe the server itself rather than the Lean compiler; do not treat it alone as compiler-version evidence. Do not change the global default toolchain or rely on machine-specific VS Code settings to repair generated output.

Prepare dependencies within the authorized environment. Do not edit PEPFlow's `pyproject.toml`, Python lockfile, or ordinary test/CI requirements for this optional task. If tools or network access are unavailable, continue source work that is possible and report affected checks as unperformed. A missing toolchain is not a mathematical counterexample.

Keep proof sources (other than the final entry), build logs, usage evidence, scratch files, and project-local caches inside `NOTEBOOK_DIR/lean/`. Project discovery configuration beside the entry or in a reused ancestor is the necessary exception. Do not add Lean code or build cells to the source notebook.

## 3. Formalize the proof and expose the final statement

Translate the existing proof structure with exact constants and coefficient definitions. Prefer reusable local identities, weighted inequalities, and square decompositions already supplied by the notebook. Prove their sign and domain conditions. Dense matrix expansion or a universal PEP-to-Lean translator is not a prerequisite.

Relevant obligations include:

- All inner-product, function-value, and constant terms; a quadratic-part identity alone may be insufficient.
- Nonnegative interpolation weights and square coefficients, PSD when used, and justified division/cancellation.
- Identification of auxiliary coefficients or transformed variables with original notebook quantities.
- General-horizon sequence properties, induction/telescoping, and correct endpoints. Sampled horizons or an assumed positive symbol do not prove these.
- For end-to-end scope, the bridge from the actual function/operator assumptions to every interpolation or optimality inequality used.

Python, SymPy, SDP outputs, and certificate data can guide proof construction. Their success flags are not Lean proof terms. Import exact data only with an in-Lean justification of the identities and inequalities it establishes.

Put definitions and supporting lemmas in the proof library. In the sibling `<stem>_lean.lean`:

1. Import the library.
2. Include a short source/scope comment and the exact check commands.
3. Declare each selected final theorem with complete hypotheses and conclusion, proved from library lemmas. Do not hide its type behind an unannotated alias or expose only a sample instance.
4. Print its type and transitive axiom dependencies with `#check @Namespace.finalTheorem` and `#print axioms Namespace.finalTheorem`, using the actual names.

If the source does not fully define the claimed statement, such as a fitted coefficient with no all-horizon definition, keep an incomplete entry documenting the missing component and record it in the report. Do not invent a coefficient or replace it with an arbitrary parameter to manufacture a complete theorem declaration.

Keep this sibling source as the canonical final check target. Do not validate a temporary copy and then edit the delivered source afterward. Identify unfinished targets as unfinished in both entry and report; a scaffold containing `sorry` is never a completed proof.

## 4. Verify the exact entry through the CLI and language server

### CLI and proof audit

Run sequentially from `PROJECT_ROOT`, using its pinned Lake executable:

```text
lake env lean --version
lake build NotebookEntry
lake env lean "<stem>_lean.lean"
```

Substitute the actual target and the entry's path relative to `PROJECT_ROOT`. `NotebookEntry` must build the delivered entry and its supporting imports. For a custom check target, ensure the library build precedes the exact entry check and failures propagate. `lake env` supplies the environment but does not build imports itself. Use tool working-directory arguments and argument arrays rather than shell concatenation. A library-only `lake build` does not establish that the final entry was checked.

Record working directory, executable, version, command, exit status, entry path/hash, and relevant logs. Inspect the actual type and axiom output for every reported theorem. Confirm the intended hypotheses and quantifiers survived translation; a weaker or vacuous statement is insufficient. Require the theorem's dependency closure to contain no `sorryAx` or problem-specific axioms replacing a proof. Standard foundations such as `propext`, `Classical.choice`, and `Quot.sound` may appear. A source scan alone does not establish this, and an empty or failed audit log is not success.

Prefer kernel-checked proof terms. Native decision procedures can add version-dependent compiler/native-evaluation trust; inspect and disclose any such dependencies rather than reporting an ordinary kernel-only result. Do not reject a library merely because a tactic implementation contains `unsafe`: the theorem's proof and axiom dependencies are the relevant boundary. Apply the validation guidance for the pinned version.

### Language-server check

After building imports, start `lake serve --` from the same `PROJECT_ROOT` with the same pinned executable/environment that normal project discovery selects. Initialize LSP with that root URI and open the exact delivered file URI with its current on-disk contents. Do not test a copy inside `lean/` or inject import paths absent from the generated project.

Use the bundled [language-server checker](../scripts/verify_lean_lsp.py), resolving its path relative to this skill before changing directories:

```text
python "<skill-dir>/scripts/verify_lean_lsp.py" --project-root "<PROJECT_ROOT>" --entry "<absolute-entry-path>" --lake "<lake-executable>" --output "<NOTEBOOK_DIR>/lean/<stem>_lsp.json"
```

The helper uses `textDocument/waitForDiagnostics` for the opened document version to wait for full processing. It records the exact file hash, completed diagnostics, and launch details; errors, unfinished-proof diagnostics, missing completion, timeouts, or server failures cannot pass. An early empty diagnostic notification, successful initialization, or simply starting `lake serve` is insufficient. Review warnings and confirm the expected theorem type/axiom audit messages arrived for all selected theorems.

If the pinned server lacks that request, use a documented equivalent completion mechanism supported by that version, with the same URI/version and final-diagnostic guarantees, or report language-server verification as unperformed with the reason. Never convert an unsupported check or timeout into a pass. Recheck the same file hash as the CLI run, and rerun both affected checks after source/configuration changes. Use incremental builds instead of routinely deleting caches.

Check the delivered layout also makes the entry discoverable by VS Code's Lean extension without manual project-configuration edits. Record GUI interaction separately: a headless language-server pass establishes the server check, not that a VS Code window was visually inspected. Normal prerequisites (Elan/the pinned toolchain and the Lean extension) still apply. Reloading a previously open window may clear a stale session, but does not substitute for correct project configuration.

Report separate outcomes for the CLI build, exact-entry compilation and axiom audit, project/toolchain discovery, and completed language-server check. Use `passed`, `failed`, or `not run` with evidence/reason for each. When only CLI verification succeeds, preserve that result and explicitly state that editor verification is incomplete; do not describe the project as fully verified for both interfaces.

Consult the official [Lake reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/), [VS Code Lean manual](https://github.com/leanprover/vscode-lean4/blob/master/vscode-lean4/manual/manual.md), and [proof validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) for version-dependent behavior.

## 5. Itemized token usage

Always include a task breakdown in `lean/<stem>_verification.md` and the completion report. Adapt these groups to the work actually performed:

| Task | Scope |
| --- | --- |
| Proof extraction and statement mapping | Notebook/supporting-file reading and target analysis |
| Lean environment and dependencies | Project preparation and library inspection |
| Supporting lemmas | Definitions, identities, positivity/PSD/sequence proofs; split substantial named lemmas when useful |
| Final theorem and entry file | Connecting results and exposing the selected statement |
| Build, editor verification, audit, and repair | CLI and language-server checks, project/toolchain discovery, statement/axiom review, and fixes |
| Reporting and coordination | Deliverables, usage reporting, and delegation coordination |
| Unallocated | Measured usage that cannot be attributed to one task |

Use actual provider/host request-level usage or valid deltas from cumulative counters, recording scope, source, and attribution boundaries as work proceeds. If the host supplies Codex JSON events, completed-turn usage can be a source; see [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode). A skill cannot guarantee that the current host exposes counters.

- Record task and worker/request identifiers with available input, output, cached-input, reasoning, and total fields. Include retries and delegated work once; do not add child totals again if a parent counter includes them.
- Follow provider definitions. Cached input may be included in input and reasoning may be included in output; do not double-count overlapping fields.
- Attribute at observable request boundaries. If one request spans tasks without finer attribution, use unallocated instead of splitting by text length, elapsed time, or intuition. Commentary or a tool boundary alone does not create a provider usage record.
- Distinguish a complete total from an observed subtotal. Reconcile complete comparable task totals plus unallocated usage with the run total when possible. A known run total does not justify inventing task totals.
- Use `unavailable` (or `null` in structured records) for unknown counts, with the reason. Mark partial coverage, including counts visible only after the final response. Do not use zero for missing data or substitute tokenizer estimates for measured usage.
- Do not launch additional model sessions or API calls merely to produce telemetry. Missing counters do not block proof work; retain the task rows with unavailable counts when that is all the host supports.

The report table shows task, measured input/output/total where available, coverage (`complete`, `partial`, or `unavailable`), and measurement source or limitation. Keep cached/reasoning details when exposed. Do not claim that the table covers all billable usage when coverage is incomplete.

## 6. Deliver and report scope accurately

Maintain one stem-specific verification report in `lean/` with source-to-statement mapping, theorem names, assumptions, pinned environment, reproduction commands, exact entry path/hash, CLI build/axiom results, project/toolchain discovery and completed language-server results, remaining gaps and unperformed checks, and the token table. Keep lengthy logs and available raw usage evidence beside it in `lean/`, referenced from the report. Do not copy unrelated conversation logs into the deliverable.

Keep mathematical status separate from the CLI/editor check outcomes above. Use these statuses per selected target:

- **Verified:** the exact delivered theorem was checked at the stated scope, with assumptions and trust dependencies disclosed.
- **Incomplete:** a required proof obligation remains open; list it and useful proved subresults.
- **Unverified source:** source was produced, but compilation or required validation was not performed.

An unavailable toolchain or unfinished formalization does not by itself refute the notebook's proof. Report any actual mathematical discrepancy separately. If only a conditional implication was checked, say so prominently rather than describing the original theorem as verified.

The final answer links the sibling entry and verification report, identifies the discoverable project root and theorem(s), gives the exact CLI and language-server check commands and outcomes (including anything not run), and includes the task-token breakdown or its explicit observability limits. Keep the source notebook unchanged unless its revision was also requested.
