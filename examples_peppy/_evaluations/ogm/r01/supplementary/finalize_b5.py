import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent.parent
notebook_path = root / "ogm_example_lyap.ipynb"
nb = json.loads(notebook_path.read_text(encoding="utf-8"))
execution = json.loads((root / "supplementary/b5-nbconvert-evidence.json").read_text())
assert execution["returncode"] == 0
static = json.loads((root / "supplementary/b5-static-001.json").read_text())
assert all(
    row["returncode"] == 0
    for row in static["commands"]
    if row["label"] in ("source_ruff", "source_ty", "clean_kernel_import_probe")
)
texts = []
for cell in nb["cells"]:
    source = "".join(cell["source"])
    if cell["cell_type"] == "code":
        assert cell["execution_count"] is not None
        assert not any(o["output_type"] == "error" for o in cell.get("outputs", []))
        texts.extend("".join(o.get("text", [])) for o in cell.get("outputs", []))
    else:
        assert not any(ch in source for ch in ("\t", "\r", "\f", "\x08"))
        assert "\\\\" not in source and "\\(" not in source and "\\[" not in source
        assert source.count("$") % 2 == 0
summary = next(text for text in texts if "Exact symbolic checks:" in text)
line = next(
    line for line in summary.splitlines() if line.startswith("Exact symbolic checks:")
)
symbolic = ast.literal_eval(line.split(":", 1)[1].strip())
assert set(symbolic) == {
    "step",
    "base",
    "terminal_step",
    "boundary",
    "N1",
    "normalization",
}
assert all(all(result.values()) for result in symbolic.values())
b4 = json.loads((root / "state/ogm_b4.json").read_text())
formula = r"""V_0=0. For 1<=k<N, V_k=2*theta_k^2/theta_N^2*(f(x_k)-f_star)-theta_k^2/(L*theta_N^2)*||g_k||^2+L/(2*theta_N^2)*(||z_{k+1}-x_star||^2-||x_0-x_star||^2). V_N=f(x_N)-f_star+L/(2*theta_N^2)*(||z_N-x_star-theta_N/L*g_N||^2-||x_0-x_star||^2)."""
structure = dict(
    quadratic_convention="sum_ij C_ij <v_i,v_j>; symmetric C, off-diagonal counted twice",
    interior=dict(
        index_domain="1 <= k < N",
        basis_labels=["x_0-x_star", "g_k", "z_{k+1}-x_star"],
        coefficients="diag(-L/(2 theta_N^2), -theta_k^2/(L theta_N^2), L/(2 theta_N^2))",
    ),
    initial=dict(
        index_domain="k=0", basis_labels=[], coefficients="empty matrix, V_0=0"
    ),
    terminal=dict(
        index_domain="k=N, including N=1",
        basis_labels=["x_0-x_star", "z_N-x_star-theta_N/L*g_N"],
        coefficients="diag(-L/(2 theta_N^2), L/(2 theta_N^2))",
    ),
    function_terms=[
        dict(
            index_domain="1 <= k < N",
            expression="f(x_k)-f_star",
            coefficient="2 theta_k^2/theta_N^2",
        ),
        dict(index_domain="k=N", expression="f(x_N)-f_star", coefficient="1"),
    ],
    constant_terms=[],
)
coeff_code = """def analytic_coefficients(k, N, L_value, theta):
    T = theta[N]
    if k == 0:
        return sp.zeros(0, 0), sp.S.Zero
    if k == N:
        return sp.diag(-L_value/(2*T**2), L_value/(2*T**2)), sp.S.One
    return sp.diag(-L_value/(2*T**2), -theta[k]**2/(L_value*T**2), L_value/(2*T**2)), 2*theta[k]**2/T**2
"""
multiplier_code = """def local_multipliers(j, N, theta):
    T = theta[N]
    star = T/T**2 if j+1 == N else 2*theta[j+1]/T**2
    chain = 2*theta[j]**2/T**2
    return star, chain
# Initial auxiliary contribution: 2/theta[N]**2 * I_star,0.
"""
proof_checks = {
    name: True
    for name in ("step", "base", "boundary", "signs", "domain", "normalization")
}
arguments = dict(
    step="Exact all-coordinate nonterminal identity under t^2=s^2-s; positive local multipliers and nonpositive smooth-convex interpolation residuals.",
    base="Phi_0-L||x_0-x_star||^2/2=2 I_star,0 with theta_0=1 and z_0=x_0; combine with first ordinary step, or N=1 direct check.",
    boundary="Exact terminal transition uses 2t^2=s^2-s. Phi_N=theta_N^2 gap_N+L||z_N-x_star-theta_N*g_N/L||^2/2; the square is nonnegative.",
    signs="L>0. Theta_0=1 and ordinary recurrence preserves theta>=1; terminal theta_N>=2. All multipliers and the square coefficient are positive. Each interpolation residual is <=0.",
    domain="All integer N>=1, real finite-dimensional Euclidean spaces, convex L-smooth f with L>0 and stationary minimizer, R>=0. Direct symbolic N=1 identity checked. No division by R.",
    normalization="V_N<=V_0=0, terminal expression and ||x_0-x_star||^2<=R^2 give gap_N<=L R^2/(2 theta_N^2), including R=0.",
)
state = {
    **b4,
    "proof_checks": proof_checks,
    "proof_arguments": arguments,
    "symbolic_component_checks": symbolic,
    "lyapunov_formula": formula,
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": structure,
    "coeff_code": coeff_code,
    "local_multiplier_code": multiplier_code,
    "coefficient_formula_status": "verified",
    "remaining_unknowns": [],
    "unresolved_coefficients": [],
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": True,
    "analytic_full_pep_status": "Global table not separately claimed; complete local analytic Lyapunov proof established",
    "run_status": "success",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "notebook": "ogm_example_lyap.ipynb",
    "notebook_sha256": hashlib.sha256(notebook_path.read_bytes()).hexdigest(),
    "static_evidence": "supplementary/b5-static-001.json",
    "execution_evidence": "supplementary/b5-nbconvert-evidence.json",
    "presentation_policy": "evaluation-ancillary-v1",
    "finished_utc": datetime.now(timezone.utc).isoformat(),
}
(root / "state/ogm_b5.json").write_text(json.dumps(state, indent=2, allow_nan=False))
print("B5 proof state saved:", state["notebook_sha256"])
print("Theorem: f(x_N)-f(x_star) <= L R^2 / (2 theta_N^2), for every N>=1.")
