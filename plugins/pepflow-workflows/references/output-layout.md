# Output Layout

Apply this policy whenever a Peppy workflow creates files. Resolve locations from the main output notebook's actual parent directory, called `NOTEBOOK_DIR` below. For a new analysis, choose the notebook destination before creating supporting files. Workflow examples such as `examples_peppy/{ALGO_NAME}/` refer to that directory; preserve any user-specified notebook location.

| Location | Contents |
| --- | --- |
| `NOTEBOOK_DIR/` | Main output notebook(s) and the required algorithm setup module. Keep an existing or explicitly requested README here; do not create one merely to describe the folder layout. |
| `NOTEBOOK_DIR/state/` | The main-step state contract: `b1` through `b5` JSON, required dense/relaxed solver results, constraint selections, and other required workflow state or certificate data. Preserve the keys and paths consumed by later steps. |
| `NOTEBOOK_DIR/supplementary/` | Additional helper modules, runner scripts, independent verification/test scripts, exploratory results, debug dumps, logs, extra Markdown/TeX documents, exported figures, and temporary notebook copies. |
| `NOTEBOOK_DIR/supplementary/.runtime/` | General Jupyter/Python runtime files and tool scratch files. Keep durable supporting files outside this runtime directory. |

## File creation rules

- Create only files needed for the requested work. Reuse the existing notebook and supporting files where appropriate; avoid duplicate reports, numbered variants, and redundant standalone reproductions of notebook content.
- Create `supplementary/` and any subdirectory only when a file actually needs it. Do not scaffold empty subfolders, inventories, or extra README files by default.
- Place new additional files under `supplementary/` from the outset. Do not use the notebook directory, `state/`, or a repository-wide build directory as a catch-all for extra files. A temporary sweep cache belongs in `supplementary/`; the final sweep results required by Block 1 remain in its state JSON.
- Resolve helper imports, state-file references, script paths, and output paths against the selected notebook directory or repository root explicitly. A script running inside `supplementary/` must still locate the main setup and `state/` correctly. Check generated references after selecting file locations.
- When creating or updating an analysis notebook, keep the theorem, proof-critical constructions, and symbolic checks visible in the main notebook. Supporting modules can aid presentation or independent checks, but must not become the sole location of essential proof reasoning.
- `supplementary/` can contain files required to rerun the notebook. Do not treat the entire directory as disposable or delete it automatically.
- Preserve existing user files and their working references. This policy governs newly created files; do not bulk-move or delete existing outputs merely to adopt the layout. Follow explicit user instructions when reorganizing files or selecting different output locations.
- Before reporting completion, inspect the files produced by the current task and confirm that main outputs, formal state, and additional files follow this layout, and that notebook/helper references still resolve.

## Proof verification files during notebook authoring

When creating a notebook or carrying out a requested proof revision, if you create or reuse a separate verification file to justify positivity or another proof condition, include the proof-critical identities and their verification in the main notebook. This applies to calculations used by the argument, not to a file merely present in an existing output directory.

For each such calculation, show the identity and its purpose; the necessary variable/coefficient definitions, assumptions, index/parameter domains, and recurrence or endpoint data; executable code constructing the actual expressions and checking them with appropriate exact arithmetic; and the executed result. Explain how the identity and justified assumptions imply the required sign or other conclusion. A zero identity residual alone does not prove positivity, and finite samples do not prove an all-horizon claim.

The calculation must be reproducible from the notebook's own cells without hidden mathematical code in the separate verifier. An external checker call, script execution, or stored Boolean/residual alone is insufficient. Generic library APIs, the required setup module, and workflow state remain allowed; their implementations need not be embedded. Reuse earlier notebook definitions and checks, placing needed details near their use or in a short notebook appendix rather than copying the whole file.

Elementary facts such as `1/k > 0` for `k >= 1` need only a clear domain and, if useful, a short explanation; do not add a dedicated lemma or verification cell. Do not create a verification file just to activate this rule. Exploration, rejected candidates, redundant independent tests, and formatting/runtime machinery can remain supplementary. Do not expand existing examples or add unrelated structural proofs merely to adopt this policy.

Apply this inclusion rule at the block's normal notebook/evidence update. Record the relevant cells and results within the existing checklist entries, without adding another checklist or state schema. Preserve the current numerical handoffs: unfinished analytic work remains explicit until its owning proof stage; this rule does not require an earlier closed-form or sign proof.
