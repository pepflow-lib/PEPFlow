# Artifact cleanup review

Date: 2026-09-25 (UTC).
Skill: `clean-peppy-artifacts`.
Scope: this 30-attempt campaign only.

## Decision

No experimental files were removed: **0 files, 0 bytes**. All **9,849 existing files (195,423,072 bytes)** were retained. This review adds only this administrative record.

The campaign is a completed, frozen experiment archive, not a disposable delivery copy. The skill requires preserving frozen attempts and assessments. No `.runtime`, `__pycache__`, browser-profile, or other cache directory eligible for removal was present. No symbolic links or reparse points were found in the inspected campaign tree.

All **42 temporary-looking candidates** were retained: 21 `_sweep_tmp.json` files appear in the frozen submission inventories, and 21 corresponding files belong to preserved review validation copies. A temporary-looking filename does not override the archive's retention rules. Authoring helpers, logs, and duplicate review copies were also preserved as parts of the archived experiment.

## Checks and pre-existing limitations

- Read the campaign manifest, completed detailed status, 30 submission inventories, reporting amendment, and controller snapshot-exclusion rules. The original stopping outcomes remain 27 completed attempts and 3 errors; this review does not revise any mathematical verdict.
- Compared all 9,849 existing files with the source Git blobs at `c02b68927031649ac91862b3c1de9a7001e421ad`; every file matched exactly. The local import was committed at `b4175be5` before this review.
- The 30 submission inventories list 4,836 paths. Of these, 423 are absent both locally and in that source commit: 420 approved workflow-snapshot files under `plugins/pepflow-workflows/`, plus 3 `.ruff_cache` files from `pgm_without_sos/r05`. These omissions predate this cleanup. No inventory was rewritten and no current skill was substituted for a missing historical snapshot. This is not a complete historical-snapshot restoration check.
- No notebook, solver, verifier, or experiment was rerun. Hash equality establishes preservation of the imported archive, not mathematical correctness or complete replayability on this machine.
- No anonymization, path rewriting, outcome adjustment, or time/token accounting change was performed.

The source archive remains identified by its original commit and campaign path. Existing submission hashes, assessments, provenance, reporting amendments, and measurements are unchanged. A future cleanup should reuse this file and avoid a timestamp-only update when nothing has changed.

## Follow-up: redundant controller copies and reviewer caches

Date: 2026-09-25T09:11:15+00:00.

Removed **10 files, 760,127 bytes**: four byte-identical controller aliases (21,053 bytes) and six reviewer-generated Matplotlib font caches (739,074 bytes). Campaign file count changes from **9,850 to 9,840**. This is administrative cleanup after generation and assessment; experimental outcomes, eligibility, timings, token accounting, and recorded hashes are not recalculated.

The earlier review above used blanket archive retention and did not distinguish the differently named reviewer scratch directories. This pass confirms actual frozen-evidence boundaries: submission inventories cover attempt output paths, not unpinned controller aliases or subsequently generated reviewer font caches. Assessment records and cited validation evidence remain unchanged.

### Removed controller aliases

Each retained version below is byte-identical to its removed alias. The archived bare paths have no live consumer or assessment-evidence pin. Historical commands refer to original tmp paths; their exact source remains available in the versioned copies. Unique controller versions, preparation tools, and access/accounting records remain.

| Removed path | Retained canonical path | SHA-256 of both |
| --- | --- | --- |
| supplementary/controller-sources/peppy_astra_collect_host.py | supplementary/controller-sources/fb9094f76753d1cf-peppy_astra_collect_host.py | fb9094f76753d1cf607f74184555236cf5a43f5ee25367ed4c577ebe6eeb873a |
| supplementary/controller-sources/peppy_astra_control.py | supplementary/controller-sources/871b7e43046a9a7e-peppy_astra_control.py | 871b7e43046a9a7eb9a0ccb6a54a9fa9c3526e447900b45f090f924f4bd86e8a |
| supplementary/controller-sources/peppy_astra_report.py | supplementary/controller-sources/1e991901fc7735cf-peppy_astra_report.py | 1e991901fc7735cf72e1d0842a727d56dc5bdb113b15744b49683e0287cc71e4 |
| supplementary/controller-sources/peppy_astra_review_schema.json | supplementary/controller-sources/76d0a221d7c8b9a1-peppy_astra_review_schema.json | 76d0a221d7c8b9a14e28207fbc9856fb01bb91e06b713ef0097a36e081a9baed |

### Removed reviewer caches

These files contain only Matplotlib FontManager metadata. The retained replay scripts create review_runtime or review-runtime scratch locations and assign MPLCONFIGDIR; they do not require existing font-cache bytes. The caches are absent from submission inventories and assessment evidence references; a campaign-wide search found no filename or SHA-256 consumer outside the caches. Review completion and absence of matching active runtimes were checked. The frozen copied notebooks, source, state, reviewer scripts, replay outputs, logs, settings and original assessment records remain.

| Removed path | Bytes | SHA-256 before removal |
| --- | ---: | --- |
| supplementary/evaluation/bppm_r05/validation/review_runtime/mplconfigdir/fontlist-v390.json | 123179 | 34e734e495486f659499cc1fb66a64eaf6c06c533dac8bffc86abe015391dbb0 |
| supplementary/evaluation/feg_r01/validation/review_runtime/MPLCONFIGDIR/fontlist-v390.json | 123179 | 050afa7d6a50a8b270de9c066b6a641657b3dfb4691bb315fae4de54796572cc |
| supplementary/evaluation/feg_r02/validation/review_runtime/mplconfigdir/fontlist-v390.json | 123179 | 45cffad3343fc193480ff114ae1ca823780a6e00dd1a9c85603d61b353010124 |
| supplementary/evaluation/ogm_r02/validation/review-runtime/fontlist-v390.json | 123179 | bedec1f46f6154b6d7f7df9cb8ba5a5f8061c863b8d5ea40129b998ed18dd674 |
| supplementary/evaluation/pgm_with_sos_r04/validation/review-runtime/mplconfigdir/fontlist-v390.json | 123179 | 78e8e7623b3a5c8d99dbae596fb14f85087688df29feea8580c80ae19254025d |
| supplementary/evaluation/pgm_with_sos_r05/validation/review_runtime/MPLCONFIGDIR/fontlist-v390.json | 123179 | 0f5c1ba1f1a73d697b0589dfa12256b054ae69c1a5cf43576eaa6359b327dcec |

### Preservation checks

- Removed the six now-empty reviewer scratch roots after re-enumerating their contents and checking containment and reparse points. Replay scripts retain their directory-creation logic.
- Rechecked all 9,850 files against the pre-cleanup inventory immediately before deletion; checked target ancestry/subtree for reparse points, absolute-path containment, candidate hashes and exclusive-read access. Used native PowerShell literal-path removal. These checks are not an atomic transaction.
- All **9,839 retained original files**, excluding this editable administrative record, matched their pre-cleanup hashes afterwards. This includes all original submissions, notebooks and saved outputs, setup/state, assessments, evidence, aggregate results and time/token records. All four canonical controller copies remain identical to their retired aliases.
- The paper_draft.pdf outside the campaign also retains its original SHA-256. No notebook, solver, mathematical verifier, renderer or experiment was run; no source pin or historical verdict was changed.
- Existing historical snapshot omissions and recorded-versus-checkout hash differences were not repaired. Current preservation checks do not certify historical completeness, successful reviewer replay, or a new experimental PASS.

Retained-subset SHA-256 before = after: a4a163e11f84f99c100640fc5db2724347ee22b28cbdfc8d63863ef3d2a7dfab. Format: ordinal-sorted UTF-8 lines relative/path|decimal_bytes|lowercase_sha256 followed by LF; removed candidates and this cleanup record are excluded.

Pre-cleanup repository commit: b8792a7db392a6ecc7916dd1d08735483b6401af. The removed paths and original hashes above identify their prior versions. Reuse this record for subsequent cleanup; no per-attempt cleanup reports were created.
