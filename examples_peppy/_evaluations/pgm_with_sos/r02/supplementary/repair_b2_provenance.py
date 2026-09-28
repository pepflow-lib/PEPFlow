import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for name in ("state/pgm_dense.json", "supplementary/b2-sparse-hypothesis1.json"):
    path = root / name
    data = json.loads(path.read_text())
    hashes = data["certificate_provenance"]["source_hashes"]
    old = next(
        k
        for k in hashes
        if k.replace("\\", "/") == "supplementary/helpers/certificate.py"
    )
    hashes["supplementary/certificate-acquisition-original.py"] = hashes.pop(old)
    data["certificate_provenance"]["operational_note"] = (
        "Original acquisition code archived byte-for-byte; current verification helper uses exact parameter values and a named max-absolute helper for static checking. Solve components unchanged."
    )
    path.write_text(json.dumps(data, indent=2))
