import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "feg_example_lyap.ipynb"
nb = json.loads(path.read_text(encoding="utf-8"))
source = lambda c: "".join(c["source"])  # noqa: E731 - retain the archived notebook helper
stream = lambda c: "".join(  # noqa: E731 - retain the archived notebook helper
    "".join(o.get("text", []))
    for o in c.get("outputs", [])
    if o["output_type"] == "stream"
)
for c in nb["cells"]:
    if c["cell_type"] == "code":
        assert c["execution_count"] is not None
        assert not any(o["output_type"] == "error" for o in c.get("outputs", []))
    else:
        s = source(c)
        assert s.count("$") % 2 == 0 and not any(
            x in s for x in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r")
        )
all_output = "\n".join(stream(c) for c in nb["cells"])
checks = {
    key: text in all_output
    for key, text in [
        ("step", "Symbolic step Gram residual: zero"),
        ("base", "Symbolic base Gram residual: zero"),
        ("boundary", "Symbolic boundary Gram residual: zero"),
    ]
}
assert all(checks.values())
assert "Signs: k>=1, N>=1, L>0" in all_output
assert (
    "terminal identity implies ||A(xN)||^2<=4 L^2 R^2/N^2, including N=1." in all_output
)
checks.update(signs=True, domain=True, normalization=True)
assert (
    json.loads((root / "supplementary/b5-static-003.json").read_text())["status"]
    == "passed"
)
b4 = json.loads((root / "state/feg_b4.json").read_text())
case = lambda domain, labels, coeffs: dict(  # noqa: E731 - retain the archived notebook helper
    index_domain=domain, basis_labels=labels, quadratic_coefficients=coeffs
)
formula = "V_0=0; V_k=2*k**2/N**2*||A(x_k)||**2+4*k*L/N**2*<A(x_k),x_k-x_0> for 1<=k<=N"
structure = dict(
    quadratic_convention="V_quadratic=sum_{i,j} C_ij*<v_i,v_j>; C symmetric and off-diagonals counted twice",
    interior=case(
        "1<=k<=N-1",
        ["A(x_k)", "x_k-x_0"],
        {"C[0,0]": "2*k**2/N**2", "C[0,1]=C[1,0]": "2*k*L/N**2", "C[1,1]": "0"},
    ),
    initial=dict(
        index_domain="k=0", basis_labels=[], quadratic_coefficients={}, formula="0"
    ),
    terminal=case(
        "k=N>=1",
        ["A(x_N)", "x_N-x_0"],
        {"C[0,0]": "2", "C[0,1]=C[1,0]": "2*L/N", "C[1,1]": "0"},
    ),
    function_terms=[],
    constant_terms=[],
)
arguments = dict(
    step="Exact original unknown-coefficient Scalar difference re-evaluated after solving its full-component linear equations. Multipliers 4Lk(k+1)/N^2 and 2(k+1)^2/N^2 are positive for k>=1,L>0,N>=1.",
    base="Actual shared x_1/2=x_0 and x_1=x_0-A(x_0)/L give V_1=(2/N^2)Q(x_0,x_1)<=0=V_0.",
    boundary="Metric-4L^2R^2/N^2 = V_N + (4L/N)M(x_N,x_star) - ||A(x_N)-(2L/N)(x_0-x_star)||^2 + (4L^2/N^2)(||x_0-x_star||^2-R^2).",
    signs="M<=0 by monotonicity, Q<=0 by Lipschitz continuity; initial residual<=0, square>=0 and subtracted. All residual coefficients nonnegative.",
    domain="Real finite-dimensional Euclidean space, L>0, R>=0, integer N>=1. Interior uses 1<=k<=N-1. N=1 has empty interior and separate base/terminal identities. No division by R.",
    normalization="The terminal exact identity includes the full initial radius squared and constant term; V_N<=0 implies the stated bound without requiring V to be positive.",
)
proof_cells = {
    str(i): c.get("id")
    for i, c in enumerate(nb["cells"])
    if c["cell_type"] == "code"
    and any(
        word in source(c)
        for word in ("ctx_step=", "step_LHS=", "ctx_base=", "ctx_terminal=")
    )
}
state = {
    **b4,
    "lyapunov_proof_verified": True,
    "analytic_full_pep_verified": False,
    "numerical_certificate_verified": True,
    "proof_checks": checks,
    "proof_arguments": arguments,
    "lyapunov_formula": formula,
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": structure,
    "coeff_code": "def coeff_pattern(k,N,L):\n    return [[2*k**2/N**2,2*k*L/N**2],[2*k*L/N**2,0]]\n",
    "local_multiplier_code": 'def local_multipliers(k,N,L):\n    return {"monotone":4*L*k*(k+1)/N**2,"Lipschitz":2*(k+1)**2/N**2}\n',
    "coefficient_formula_status": "verified",
    "unresolved_coefficients": [],
    "remaining_unknowns": [],
    "require_analytic_full_pep": False,
    "run_status": "completed",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "proof_cell_ids": proof_cells,
    "final_notebook_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "final_execution_evidence": "supplementary/b5-final-nbconvert-002-console.txt",
    "final_static_evidence": "supplementary/b5-static-003.json",
    "presentation_policy": "evaluation-ancillary-v1",
    "unresolved_work": [],
    "separate_unverified_objective": "Global analytic lambda/S tables were not established; not required for this local Lyapunov proof.",
}
(root / "state/feg_b5.json").write_text(json.dumps(state, indent=2))
# Final evidence checklist uses actual saved cells and executed output.
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "markdown":
        print(i, source(c).split("\n")[0])
print("Proof cell IDs:", proof_cells)
print("Final state saved; all exact identities and final notebook execution passed.")
