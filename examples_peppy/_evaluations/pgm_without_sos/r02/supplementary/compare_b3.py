# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
from pgm_setup import (  # noqa: F401 -- Required by exec of b3_check_code.py.
    get_pep_setup,
)

notebook_dir = runtime.ROOT
samples = []
for sample_path in ["state/pgm_b2.json", "supplementary/certificate-n6/pgm_b2.json"]:
    certificate = json.loads((notebook_dir / sample_path).read_text())
    for filename in [
        "b3_check_code.py",
        "b3_decomposition_code.py",
        "b3_grouping_code.py",
    ]:
        source = (notebook_dir / "supplementary" / filename).read_text(
            encoding="utf-8-sig"
        )
        exec(compile(source, filename, "exec"))
    observation = dict(
        N=N,
        certificate_id=certificate["certificate_id"],
        certificate_path=sample_path,
        recipe_id="reverse_ldl_latest_iterate",
        rank_profile=ranks,
        rank_convention={
            "tolerance": 1e-4,
            "scaling": "absolute unscaled original PEP Gram coordinates",
            "coordinate_order": "setup earlier-iterate first",
        },
        singular_values=singular_values,
        rank_credible=rank_credible,
        certificate_checked=certificate_checked,
        grouping_checked=grouping_checked,
        coverage_residuals=coverage_residuals,
        increment_residuals=increment_residuals,
        term_assignment=term_assignment,
        S_assignment=S_assignment,
    )
    samples.append(observation)
    (notebook_dir / f"supplementary/b3-observation-n{N}.json").write_text(
        json.dumps(observation, indent=2)
    )
print("Cross-horizon profiles:", [(s["N"], s["rank_profile"]) for s in samples])
(notebook_dir / "supplementary/b3-comparison.json").write_text(
    json.dumps(samples, indent=2)
)
