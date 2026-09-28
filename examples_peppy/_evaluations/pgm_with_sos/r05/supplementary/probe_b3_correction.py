import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
np = importlib.import_module("numpy")
for n, p in [
    (4, ROOT / "state" / "pgm_b2.json"),
    (6, ROOT / "supplementary" / "N6" / "pgm_b2.json"),
]:
    c = json.loads(p.read_text())
    S = np.array(c["S_matrix"])
    pieces = np.array(c["numerical_decomposition"]["pieces"])
    error = S - sum(pieces)
    revised = pieces[-1] + error
    print(
        n,
        "correction norm",
        np.linalg.norm(error),
        "last adjusted eig",
        np.linalg.eigvalsh(revised),
        flush=True,
    )
