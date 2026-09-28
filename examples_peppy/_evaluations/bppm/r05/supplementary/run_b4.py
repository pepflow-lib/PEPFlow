# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Replay B3 and discover the B4 basis and complete expression structure."""

import hashlib  # noqa: F401 -- Required by exec of bppm_b3.json#certificate_check_code.
import importlib.util
import json
import os
import sys
from pathlib import Path

notebook_dir = Path(__file__).resolve().parents[1]
REPO_ROOT = notebook_dir / "supplementary/approved"
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    path = notebook_dir / "supplementary/.runtime" / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
sys.path[:0] = [str(REPO_ROOT), str(notebook_dir / "supplementary/helpers")]
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup

import pepflow as pf  # noqa: E402, F401 -- Required by exec of bppm_b3.json#certificate_check_code. Paths initialized above.

# Preserve the recorded import initialization order.
# isort: split
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from certificate_tools import (  # ty: ignore[unresolved-import]  # noqa: E402, F401 -- Required by exec of bppm_b3.json#certificate_check_code. Paths initialized above.
    certificate_id,
    inventory,
    verify_certificate,
)

# Preserve the recorded import initialization order.
# isort: split
from certificate_tools import (  # ty: ignore[unresolved-import]  # noqa: E402, F401 -- Required by exec of bppm_b3.json#certificate_check_code. Paths initialized above.
    scalar_from_gram,
)

b3 = json.loads((notebook_dir / "state/bppm_b3.json").read_text())
certificate = b3
N_int = b3["N_verify"]
params_sp = {k: sp.S(v) for k, v in json.loads(b3["params_json"]).items()}
spec = importlib.util.spec_from_file_location(
    "bppm_setup", notebook_dir / "bppm_setup.py"
)
assert spec is not None and spec.loader is not None
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
f, h = setup.f, setup.h
ctx, pb, obj = setup.get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(b3["relaxed_constraints"])
for key in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(compile(b3[key], key, "exec"))
assert ranks == b3["rank_profile"]
assert b3["rank_search"]["status"] == "confirmed"
assert (
    json.loads((notebook_dir / b3["rank_search"]["evidence_path"]).read_text())[
        "summary"
    ]
    == b3["rank_search"]
)
for k, V in enumerate(lyap):
    v = pm.eval_scalar(V)
    for actual, saved in (
        (v.inner_prod_coords, b3["lyap_inner_prod_coords"][k]),
        (v.func_coords, b3["lyap_func_coords"][k]),
        (v.offset, b3["lyap_offsets"][k]),
    ):
        assert np.allclose(
            np.asarray(actual, dtype=float),
            np.asarray(saved, dtype=float),
            atol=1e-4,
            rtol=1e-5,
        )
sources = {}
for kind in ("scan", "basis", "coefficients"):
    source = (notebook_dir / f"supplementary/b4_{kind}.py").read_text()
    sources[kind] = source
    exec(compile(source, f"b4_{kind}.py", "exec"))
structure_source = (
    "function_sample_coefficients = "
    + repr(function_sample_coefficients)
    + "\n\n"
    + sources["coefficients"][
        sources["coefficients"].index("def V_k_structure") : sources[
            "coefficients"
        ].index("component_residuals={}")
    ]
)
coeff_source = sources["coefficients"][
    sources["coefficients"].index("def coeff_pattern") : sources["coefficients"].index(
        "formula_residuals={}"
    )
]
state = {
    **b3,
    "basis_templates": [
        "empty for k=0",
        "[x_star-x_0, x_star-x_k, grad_h(x_0), grad_h(x_k)] for 1<=k<=N",
    ],
    "basis_code": sources["basis"],
    "structure_code": structure_source,
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": coeff_source,
    "coefficient_formula_status": "candidate",
    "unresolved_coefficients": [],
    "expression_structure": {
        "quadratic_convention": "sum_ij C_ij <v_i,v_j>; symmetric C; off-diagonal entries counted twice",
        "interior": {
            "index_domain": "1 <= k <= N-1",
            "basis_labels": ["a_0", "a_k", "q_0", "q_k"],
            "coefficients": {
                "C02=C20": "1/(2*alpha*N)",
                "C13=C31": "-1/(2*alpha*N)",
                "others": "0",
            },
        },
        "initial": {
            "index_domain": "k=0",
            "basis_labels": [],
            "coefficients": {},
            "formula": "0",
        },
        "terminal": {
            "index_domain": "k=N",
            "basis_labels": ["a_0", "a_N", "q_0", "q_N"],
            "coefficients": "same pattern as interior",
        },
        "function_terms": [
            {
                "index_domain": "1<=k<=N",
                "expression": "f(x_k)-f(x_star)",
                "coefficient": "k/N",
            },
            {
                "index_domain": "1<=k<=N",
                "expression": "h(x_0)-h(x_k)",
                "coefficient": "1/(alpha*N)",
            },
        ],
        "constant_terms": [],
    },
    "numerical_reconstruction": {
        "certificate_id": b3["certificate_id"],
        "required_indices": list(range(N_int + 1)),
        "quadratic_residuals": coefficient_residuals,
        "component_residuals": component_residuals,
        "tolerances": {
            "indep_tol": 1e-7,
            "span_tol": 1e-5,
            "component_atol": 1e-4,
            "component_rtol": 1e-5,
        },
        "passed": True,
    },
    "candidate_formula_residuals": formula_residuals,
    "function_sample_coefficients": function_sample_coefficients,
    "completion_status": "pending_notebook_checks",
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(notebook_dir / "state/bppm_b4.json").write_text(json.dumps(state, indent=2))
(notebook_dir / "supplementary/b4-search.json").write_text(
    json.dumps(
        {
            "candidate_labels": [p[0] for p in unique_pairs],
            "spanning": {
                str(k): [candidate_labels[id(v)] for v in vals]
                for k, vals in spanning_by_k.items()
            },
            "searched_bases": {
                str(k): [candidate_labels[id(v)] for v in vals]
                for k, vals in sparse_basis_by_k.items()
            },
            "searched_coefficients": {
                str(k): v.tolist() for k, v in sparse_coeff_by_k.items()
            },
        },
        indent=2,
    )
)
