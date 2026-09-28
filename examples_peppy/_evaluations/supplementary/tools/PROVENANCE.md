# Sources, environment and verification scope

## Experimental records

The six condition directories contain the 30 paper submissions. Original reviews, timing/token measurements and the final post hoc assessment remain linked in [the attempt index](../../attempts.md). The final mathematical verdict is 30 PASS, while original completed delivery is 27/30. Packaging checks do not replace either historical count or the recorded costs.

Published file hashes and their historical references are described in [PUBLICATION.md](PUBLICATION.md) and [publication-manifest.json](publication-manifest.json). Recorded paths and storage metadata have been prepared for this checkout; historical submission pins remain as evidence of the recorded versions.

## Shared framework

The campaign recorded framework revision `8be0f10af0ff415639447aaeb9fa58a826c81b2a`. All 39 source entries have been recovered with exact historical SHA-256 values in [framework/](framework/). [framework-manifest.json](framework-manifest.json) records their origin and byte hashes.

The 23 common Python source files are stored once. [shared-files.json](shared-files.json) describes their 690 trial locations and reproduces the original published trial bytes, including line endings. Replay restores those files into working copies before applying historical inventory checks. It also recovers the 420 omitted workflow-copy paths from the same snapshot; three missing Ruff cache entries remain irrelevant to the proof code.

## Historical hash differences

Run `python examples_peppy/_evaluations/supplementary/tools/audit_archive.py --check` from the repository root to verify [archive-audit.json](archive-audit.json). Its categories distinguish archived byte matches, newline reconstruction, documented publication correspondence and unresolved differences. Maintained sources are first validated and reversed through [source-edits.json](source-edits.json); the audit identifies their physical current hashes separately from the archived comparison view.

One primary notebook matches its historical hash after newline reconstruction; the other 29 have documented pre-publication hashes matching their historical pins after newline reconstruction. The 4,559 mapped validation records retain 854 unexplained historical differences. Six of nine evaluation-protocol hashes have not been recovered at their exact recorded version. Shared storage does not resolve these discrepancies or imply that the corresponding proofs failed.

Both artifact restoration maps specify exact output bytes. When a canonical shared source uses different line endings, the map explicitly records the conversion. These maps reconstruct review copies; their earlier cleanup summaries remain historical records.

## Environment and execution

[historical-environment.json](historical-environment.json) records the available generation environment: Windows, Python 3.11.13 and the recorded library versions. Generation and independent review used GPT-6 Astra with medium reasoning, at most three concurrent workers, a two-hour limit per attempt/review and no token cap. The clean-room policy was instruction-based, without filesystem read isolation.

Current saved-code replay uses the separate pinned Python 3.11.14 environment in [replay-environment-win-py311.txt](replay-environment-win-py311.txt). It does not repeat AI generation or reproduce model timings. [validation.md](validation.md) records actual execution coverage, source-hash failures and symbolic-only limits. Cross-platform execution has not been established.
