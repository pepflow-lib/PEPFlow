# B1 access and operational record

Access control: instruction_only; no exhaustive OS tracing. No prohibited material observed or knowingly used.

Direct approved reads: dispatch.md, input.md, worker-protocol.md; pep-implement/SKILL.md and references/workflow.md; pep-full-proof/SKILL.md; lyap-define/SKILL.md; lyap-vectors/SKILL.md; lyap-closed-form/SKILL.md; plugins/pepflow-workflows/references/output-layout.md; pepflow/operator.py, pep_runner.py, pep.py, solver.py, pep_result.py, __init__.py; plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py. Earlier generic reads are in preflight-access-record.json. All these paths are under supplementary/approved. Approved framework runtime imports and adapter copied-source manifests are in preflight/static JSON evidence.

Own generated resources consulted: feg_setup.py; supplementary/b1_sweep.py, _sweep_tmp.json, b1_notebook.py; feg_example_lyap.ipynb; state/feg_b1.json; supplementary/static-repaired-arguments.json; supplementary/b1-static-003.json. All commands used the attempt root, pinned interpreter with -I -B, and approved/own import roots. Commands consisted of exact-file Get-Content/rg inspections, PowerShell creation/editing of own files, b1_sweep.py and b1_notebook.py execution, and the approved adapter using recorded settings/arguments. Actual command outputs are retained in supplementary/*output*.txt; adapter commands/versions/roots/manifests are preserved in individual JSON evidence.

Operational incidents and repairs:
- Windows default text encoding produced a SyntaxError in the newly generated notebook-author script. Converted own script to UTF-8 and reran successfully (b1-notebook-output-002.txt).
- Broad supplementary helper staging hit Windows path-length limits (b1-static-001.json). Narrowed own helper root to supplementary/helpers and probe path accordingly. Generic preflight-002.json passed. No frozen source edited.
- PowerShell JSON-array argument reconstruction caused a launcher argv error before the adapter (b1-static-output-002.txt; no corresponding JSON was created). Rebuilt argv from approved settings, as in the initial successful invocation.
- Ruff reported E402 in the bootstrap/import cell (b1-static-003.json). Split notebook path bootstrapping from imports, reran the notebook in a fresh pinned kernel, and repeated checks without suppression.
- Jupyter emitted a Windows selector-thread compatibility warning; notebook execution succeeded. No rendering was attempted under evaluation-ancillary-v1.

Mathematical status: B1 sweep only, CLARABEL defaults, optimal at N=1..7. No B2 solve or other later-block mathematical work performed. Numerical comparison residual at N=2..7: 8.768811288195622e-09. The theorem remains unproved.
