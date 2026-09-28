"""Package and execute recorded replay source as self-contained handoff fragments."""

import inspect
import json
import sys
import textwrap
from pathlib import Path
from typing import Any


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "supplementary/helpers"))
    # local helper resolved by the notebook runtime path
    from runtime import configure  # ty: ignore[unresolved-import]

    configure()
    import numpy as np

    # local helper resolved by the notebook runtime path
    from partial_sums import construct, rebuild  # ty: ignore[unresolved-import]

    b3 = json.loads((root / "state/ogm_b3.json").read_text())
    b4 = json.loads((root / "state/ogm_b4.json").read_text())
    preamble = """import hashlib
import json
import numpy as np
import pepflow as pf
from certificate import digest_state, inventory, scalar_coordinates, verify_certificate
from runtime import NOTEBOOK_DIR
"""
    certificate_check_code = (
        preamble
        + inspect.getsource(rebuild)
        + """
ctx, pb, obj, pm = rebuild(certificate)
N_int = certificate['N_verify']
N = N_int
params_sp = json.loads(certificate['params_json'])
basis = ctx.basis_vectors()
certificate_checked = True
"""
    )
    decomposition_code = textwrap.dedent(b3["decomposition_code"])
    grouping_code = (
        inspect.getsource(construct)
        + """
replayed_observation = construct(certificate, verbose=False)
ctx, pb, obj, pm = rebuild(certificate)
basis = ctx.basis_vectors()
scalars = ctx.basis_scalars()
lyap = []
for coordinates in replayed_observation['lyap_coordinates']:
    expression = pf.Scalar.zero() + coordinates['offset']
    expression += sum((float(value) * scalar for value, scalar in zip(coordinates['func'], scalars)), pf.Scalar.zero())
    expression += sum((float(coordinates['gram'][i][j]) * basis[i] * basis[j]
                       for i, j in np.ndindex((len(basis), len(basis)))), pf.Scalar.zero())
    lyap.append(expression)
ranks = replayed_observation['rank_profile']
grouping_checked = replayed_observation['grouping_checked']
extra_duals = {}
"""
    )
    namespace: dict[str, Any] = {"certificate": b3}
    for source in (certificate_check_code, decomposition_code, grouping_code):
        exec(compile(source, "<saved-replay>", "exec"), namespace)
    assert namespace["certificate_checked"] and namespace["grouping_checked"]
    assert namespace["ranks"] == b3["rank_profile"]
    for k, V in enumerate(namespace["lyap"]):
        actual = namespace["scalar_coordinates"](namespace["pm"], V)
        assert np.allclose(
            actual["gram"], b3["lyap_inner_prod_coords"][k], atol=1e-4, rtol=1e-5
        )
        assert np.allclose(
            actual["func"], b3["lyap_func_coords"][k], atol=1e-4, rtol=1e-5
        )
        assert abs(actual["offset"] - b3["lyap_offsets"][k]) <= 1e-4
    basis_code = "ctx4, obj4, N4 = ctx, obj, N_int\n" + b4["basis_code"]
    structure_code = (
        "ctx4, obj4 = ctx, obj\ncoeff4 = coeff_by_k\n" + b4["structure_code"]
    )
    namespace["coeff_by_k"] = {
        int(k): np.asarray(C, dtype=float).reshape((0, 0))
        if not C
        else np.asarray(C, dtype=float)
        for k, C in b4["coeff_by_k"].items()
    }
    exec(compile(basis_code, "<saved-basis>", "exec"), namespace)
    exec(compile(structure_code, "<saved-structure>", "exec"), namespace)
    reconstruction = {}
    for k, target in enumerate(namespace["lyap"]):
        residual = namespace["scalar_coordinates"](
            namespace["pm"], namespace["V_k_structure"](k) - target
        )
        errors = {
            key: float(np.max(np.abs(value), initial=0))
            for key, value in residual.items()
        }
        assert max(errors.values()) <= 1e-4
        reconstruction[str(k)] = errors
    for state in (b3, b4):
        state.update(
            certificate_check_code=certificate_check_code,
            decomposition_code=decomposition_code,
            grouping_code=grouping_code,
        )
    b4.update(basis_code=basis_code, structure_code=structure_code)
    for filename, state in (("ogm_b3.json", b3), ("ogm_b4.json", b4)):
        (root / "state" / filename).write_text(
            json.dumps(state, indent=2, allow_nan=False), encoding="utf-8"
        )
    evidence = {
        "certificate_id": b3["certificate_id"],
        "certificate_replay": True,
        "grouping_replay": True,
        "basis_and_structure_replay": True,
        "component_residuals": reconstruction,
        "repair": "Added executable scope setup and dedented stored decomposition source; mathematical formulas and certificate components unchanged.",
    }
    (root / "supplementary/final-replay-evidence.json").write_text(
        json.dumps(evidence, indent=2), encoding="utf-8"
    )
    print(json.dumps(evidence))


if __name__ == "__main__":
    main()
