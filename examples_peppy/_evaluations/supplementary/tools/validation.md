# Execution and integrity checks

Checked on 2026-09-28 in the consolidated experiment layout. These checks are separate from the original model runs, reviews and generation costs. [Machine-readable results](replay-validation.json) retain the executed units, source hashes, shared-file preparation and failures.

## Data and tools

- The archived bytes of all 30 primary submitted notebooks remain recoverable after source maintenance. All 33 notebooks retain their outputs, execution counts, metadata and non-code cells; all 867 code cells retain the same executable syntax as before the type-checking edits. Table 2 values and input hashes are unchanged.
- The 23 common Python sources are stored once. All 690 trial files reconstruct exactly to their recorded bytes; they are materialized only in disposable execution copies.
- All 39 recovered framework files match their historical hashes. The audit retains 854 unexplained mapped validation differences and six differing protocol hashes, as described in [PROVENANCE.md](PROVENANCE.md).
- All 64 tool tests pass, including shared-source tampering, source-edit reconstruction, unsafe paths, and restoration conflicts.
- All 5,019 entries across both restoration maps match their declared output bytes. Fresh copies of BPPM `r01`, FEG `r03` and PGM without SOS `r02` contain 190, 168 and 152 files respectively, each independently compared with its source. Restoring files does not execute their proofs.

## Saved-code execution

Each fresh run used Python 3.11.14 on Windows in the [pinned environment](replay-environment-win-py311.txt), with active assertions, audited imported sources and no new CVXPY solve. Each trial received its 23 shared Python source files before execution.

| First repetition | Selected symbolic checks | Full notebook |
|---|---|---|
| BPPM `r01` | Completed | Stopped at the setup source-hash assertion |
| Dual FEG `r01` | Completed | Stopped at the setup/certificate-helper source-hash check |
| FEG `r01` | Completed | Completed all 26 code cells |
| OGM `r01` | Completed | Stopped at the setup/certificate-checks source-hash assertions |
| PGM with SOS `r01` | Completed | Stopped at the setup/candidates-helper source-hash assertions |
| PGM without SOS `r01` | Completed | Stopped at the additional N=6 certificate runtime-helper source-hash assertion |

A `completed` status means all units selected by that mode executed. It is not a replacement mathematical verdict. The original notebook-internal source-hash assertions remain active.

The symbolic plans retain the original derivations and assertions, with documented exclusions: BPPM and Dual FEG omit numerical-certificate linkage preludes; OGM omits its final numerical-success prose. FEG and PGM without SOS run submitted proof scripts, while the other conditions use specified notebook cells or cell segments. OGM and PGM with SOS also contain sign/domain reasoning in Markdown that has not been converted into additional executable checks.

Only `r01` of each condition was freshly executed. Other repetitions retain their [historical reviews](../../attempts.md). No AI generation, model timing replication, cross-platform validation or conjecture experiment is claimed. Commands are in [README.md](README.md).

## Static checks and source maintenance

The maintained sources pass `ty` 0.0.84, Ruff 0.12.4 lint and formatting checks, and isort 6.0.1. The complete maintained suite passes 224 tests (145 library, 15 workflow plugin and 64 supplementary tool tests) under pytest 8.4.1 on Python 3.11.14. Collection through `pytest`, `pytest .` and `python -m pytest` includes the same 224 tests and resolves the checkout package. Archived trial programs are excluded from pytest directory discovery because they execute experiment code at import. The run reports 43 warnings about sparse-matrix conversion, context/tag reuse and CVXPY accuracy; warning filters, solver settings and test tolerances are unchanged. The 39 frozen framework files are excluded from these checks and retain their exact historical hashes. Type annotations, loader guards and documented diagnostic-specific exceptions preserve the recorded mathematical expressions and assertions. Imports required by dynamically executed fragments are retained even when a linter cannot see their use.

[source-edits.json](source-edits.json) preserves the exact earlier publication bytes without a second source tree. The audit checks both physical current files and their reconstructed archived versions before comparing historical pins. The machine-readable saved-code results above remain the record of the earlier validation run; their recorded tool hashes are not rewritten to describe the maintained tools.

On Python 3.11.14, the existing strict JSON comparison in `table2.py --check` differs in two aggregate floating-point tails (`88247.85290800002` versus stored `88247.852908`, and `10331.868014999998` versus stored `10331.868015`). The row measurements, input hashes and rendered table are unchanged. The calculation and stored values have been preserved.

After source maintenance, the six selected `r01` symbolic plans completed again in the existing Windows Python 3.11.14 environment with active assertions and no solver calls. No full-notebook completion claim is added; the table above retains the earlier full-notebook results.
