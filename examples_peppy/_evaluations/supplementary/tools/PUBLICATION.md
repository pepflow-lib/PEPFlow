# Archived publication hashes

[publication-manifest.json](publication-manifest.json) records the correspondence between imported records and published files. Recorded paths and storage metadata affect file hashes; the historical submission inventories are retained separately. The public manifest records declared correspondence and does not reconstruct the private imported bytes.

Python and notebook source maintenance is recorded in [source-edits.json](source-edits.json). Each entry checks the current file hash and size, reverses the recorded UTF-8 byte edits, and checks the archived hash and size. The archived version is the publication at commit `5e56d6dd052808075dba86e18f00f1e22e8bc86c`. Replay and review-copy restoration use these verified archived bytes; the working files remain available for static checking. Historical inventories, recorded results and the publication manifest are unchanged. Archive reports identify both the maintenance manifest and the comparison view.

The common framework is stored once in [framework/](framework/). [shared-files.json](shared-files.json) identifies 690 logical trial files, their shared sources, required line endings and exact hashes. Replay materializes those files in disposable working copies. The original evaluation and post hoc restoration maps also use these shared sources.

[audit_archive.py](audit_archive.py) checks published hashes, shared-file reconstruction and the disclosed historical differences. [The validation record](validation.md) describes the checks actually executed. None of these storage checks is a mathematical proof verdict.
