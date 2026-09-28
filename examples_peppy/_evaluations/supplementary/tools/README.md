# Calculate results and execute saved checks

Run these commands from the repository root. [The experiment guide](../../README.md) links the result table and all 30 submissions.

## Table and source checks

Python 3.10 or later with the standard library is sufficient:

```sh
python examples_peppy/_evaluations/supplementary/tools/table2.py --check
python examples_peppy/_evaluations/supplementary/tools/audit_archive.py --check
```

The first command recomputes [Table 2](../../table2.md) from 30 runs, 150 block records and the final assessment. Running it without `--check` regenerates the two table files in the experiment root. The second checks the disclosed file-hash baseline, including shared sources and historical differences described in [PROVENANCE.md](PROVENANCE.md). Neither command establishes mathematical proof validity.

## Execute the selected symbolic checks

Create a separate environment and run the six first repetitions:

```powershell
uv venv --python 3.11.14 .runtime/replay-env
uv pip install --python .runtime/replay-env/Scripts/python.exe -r examples_peppy/_evaluations/supplementary/tools/replay-environment-win-py311.txt
python examples_peppy/_evaluations/supplementary/tools/replay.py --python .runtime/replay-env/Scripts/python.exe --r01 --proof-only --use-imported-sources --timeout 600
```

The runner prepares disposable copies under `.runtime/peppy-replay/`. It restores each trial's common Python sources from the single [framework snapshot](framework/) using [shared-files.json](shared-files.json), and reconstructs omitted workflow files. The published notebooks and recorded outputs are preserved. Original source pins remain active; `--use-imported-sources` allows only differences already disclosed in the audit with matching current hashes.

- `--proof-only` executes the inspected symbolic proof units for `r01` of each condition. The report identifies the exact cells, scripts and excluded scope. It does not establish the original numerical-certificate linkage or every sign argument in Markdown.
- `--trial pgm_without_sos/r02` selects one trial in full-notebook mode. Repeat `--trial` for several, or use `--all` for all 30. Proof-only plans cover `r01` only.
- Omitting `--proof-only` attempts every notebook code cell and stops on a failure, including an original source-hash assertion.
- `--timeout` applies to each trial. New CVXPY solves are blocked unless `--allow-solve` is explicitly supplied. No mode invokes an AI agent.

The output directory contains preparation reports, execution logs, results and `summary.json`. Nonzero exit status means a requested run did not finish. A `completed` status means all selected units executed, not a replacement mathematical PASS verdict. Actual results and limitations are in [validation.md](validation.md).

The tested environment is Windows with Python 3.11.14; its direct requirements and full package pins are provided here. On Unix-like systems use `.runtime/replay-env/bin/python`; that platform has not been validated. A Python audit hook blocks common accidental writes outside the disposable directories and common process/network calls; it is not an OS sandbox.

## Restore secondary review copies

The original restoration helpers accept a fresh destination. For example:

```sh
python examples_peppy/_evaluations/supplementary/restore-artifacts.py --scope bppm_r01 --destination .runtime/review-bppm
python examples_peppy/_evaluations/posthoc_20260924T024014Z/restore-artifacts.py --case feg_r03 --out .runtime/review-feg
```

These commands reconstruct files with the hashes in their maps, including declared line endings for shared sources. They do not execute the reconstructed proofs.

## Tool tests

```sh
python -m unittest discover -s examples_peppy/_evaluations/supplementary/tools/tests -v
```
