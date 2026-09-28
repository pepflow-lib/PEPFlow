# Execution and integrity checks

Checked on 2026-09-28 in the consolidated experiment layout. These checks are separate from the original model runs, reviews and generation costs. [Machine-readable results](replay-validation.json) retain the executed units, source hashes, shared-file preparation and failures.

## Data and tools

- All 30 primary submitted notebooks remain byte-identical after consolidation. Table 2 values and input hashes are unchanged.
- The 23 common Python sources are stored once. All 690 trial files reconstruct exactly to their recorded bytes; they are materialized only in disposable execution copies.
- All 39 recovered framework files match their historical hashes. The audit retains 854 unexplained mapped validation differences and six differing protocol hashes, as described in [PROVENANCE.md](PROVENANCE.md).
- All 48 tool tests pass, including shared-source tampering, unsafe paths, and restoration conflicts.
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
