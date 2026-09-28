# Published file hashes

[publication-manifest.json](publication-manifest.json) records the correspondence between imported records and published files. Recorded paths and storage metadata affect file hashes; the historical submission inventories are retained separately. The public manifest records declared correspondence and does not reconstruct the private imported bytes.

The common framework is stored once in [framework/](framework/). [shared-files.json](shared-files.json) identifies 690 logical trial files, their shared sources, required line endings and exact hashes. Replay materializes those files in disposable working copies. The original evaluation and post hoc restoration maps also use these shared sources.

[audit_archive.py](audit_archive.py) checks published hashes, shared-file reconstruction and the disclosed historical differences. [The validation record](validation.md) describes the checks actually executed. None of these storage checks is a mathematical proof verdict.
