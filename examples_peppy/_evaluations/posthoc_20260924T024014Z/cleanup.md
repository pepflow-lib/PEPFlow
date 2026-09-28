# Post-hoc artifact cleanup — 2026-09-26

Scope: posthoc_20260924T024014Z/ within the frozen 30-attempt campaign. This is a later storage cleanup, not a new assessment. The original submissions, campaign timing/token records, results.md, post-hoc mathematical verdicts, raw access/event records, validation results, and manuscript were not changed.

| Removal | Files | Bytes |
| --- | ---: | ---: |
| Exact secondary validation copies of the FEG r03 and PGM without SOS r02 primary attempts | 279 | 3,979,435 |
| Disposable Matplotlib font cache | 1 | 123,179 |
| Empty failed-output placeholder | 1 | 0 |
| **Total** | **281** | **4,102,614** |

The 279 omitted files are reproducible byte-for-byte from the retained primary attempts. [artifact-map.json](artifact-map.json) records each campaign-relative destination, canonical source, byte length, and SHA-256. [restore-artifacts.py](restore-artifacts.py) verifies all sources and destinations before copying independent files. From the campaign directory, restore a review's historical validation layout with:

    python -B posthoc_20260924T024014Z/restore-artifacts.py --case feg_r03
    python -B posthoc_20260924T024014Z/restore-artifacts.py --case pgm_without_sos_r02

For an independent copy, append --out <fresh-campaign-root> to either command. The original feg/r03/ and pgm_without_sos/r02/ primary files, with the exact mapped hashes, must accompany any distribution that relies on restoration. Historical review paths into validation/ resolve after that step. The removed font cache and empty placeholder are not reconstructed.

Retained candidates include all nine host access/event records and original-inventory.json because they support the access, chronology, and original-file-integrity claims. The two new reviews, their distinct validation scripts/results/logs, the assessment and cost records, the original summary, and policy/version records also remain. Previously recorded inventory totals and final-validation.json describe the pre-cleanup historical snapshot; they are not claims that the compact on-disk tree has the same file count.

Checks performed: all 279 secondary/canonical pairs matched byte-for-byte before removal; all remaining imported files matched the source Git blobs afterward; all mapped canonical SHA-256 values still matched; both selected validation trees were restored in a fresh temporary directory and all 279 restored hashes matched; 59 relative references in the two reviews resolved in those reconstructed trees. Idempotent restoration, conflicting-destination refusal, and overlapping-destination refusal passed. The 39 direct links in results.md and report.md remained available. No solver search, notebook execution, or new mathematical review was performed.
