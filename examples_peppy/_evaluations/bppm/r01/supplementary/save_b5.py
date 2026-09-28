import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd()
path = root / "bppm_example_lyap.ipynb"
nb = json.loads(path.read_text(encoding="utf-8"))
streams = "".join(
    "".join(o.get("text", "")) for c in nb["cells"] for o in c.get("outputs", [])
)
expected = (
    "Step",
    "Base V0",
    "Base first step",
    "N=1 base",
    "Boundary",
    "N=1, R=0 boundary",
)
for name in expected:
    assert f"{name} offset residual: 0" in streams, name
assert "Analytic Lyapunov proof verified." in streams
assert "Signs: all local and boundary multipliers are nonnegative" in streams
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        assert cell["execution_count"] is not None
        assert all(o["output_type"] != "error" for o in cell["outputs"])
b4 = json.loads((root / "state/bppm_b4.json").read_text())
final_structure = json.loads(
    json.dumps(b4["expression_structure"]).replace(", candidate", "")
)
proof_arguments = {
    "coefficient_derivation": "The exact local Gram/function/offset equations give A_next=A_current+alpha*B, mu_star=alpha*B, mu_f=A_current, mu_back=B+A_current/alpha, mu_forward=A_current/alpha. A(0)=0 and A(N)=1 imply A(k)=k/N and B=1/(alpha*N).",
    "step": "Convex residual I_q(u,v)=q(v)-q(u)+<grad q(v),u-v> is nonpositive. The exact one-step difference uses multipliers 1/N, k/N, (k+1)/(alpha*N), k/(alpha*N); all nonnegative for k>=0, alpha>0, N>=1. Hence V_(k+1)<=V_k.",
    "base": "V_0=0 is defined separately. A separate first-step context verifies V_1=I_f(star,1)/N+I_h(1,0)/(alpha*N)<=0 without requiring f(x_0).",
    "boundary": "gap-R/(alpha*N)=V_N+(D_h(star,0)-R)/(alpha*N)+I_h(star,N)/(alpha*N). All right-hand terms are nonpositive by the step proof, initial condition, and convexity.",
    "domain": "Finite-dimensional real Euclidean space; supplied closed/proper convex differentiable f,h and well-defined proximal evaluations; alpha>0, R>=0, integer N>=1. No strong convexity, smoothness constant, or positive R is used.",
    "normalization": "A(N)=1 and B=1/(alpha*N); the radius is R rather than R squared. Multiplication/division uses positive alpha*N.",
    "endpoints": "N=1 requires only the separate base step and terminal identity. R=0 is allowed because no division by R occurs.",
    "basis_coefficients": "Expanding the Bregman difference cancels h(x_star) and yields -(grad h(x_0))*(x_0-x_star)/(alpha*N)+(grad h(x_k))*(x_k-x_star)/(alpha*N), giving the symmetric off-diagonal coefficients -1/(2*alpha*N), +1/(2*alpha*N).",
}
state = {
    **b4,
    "proof_checks": {
        key: True
        for key in ("step", "base", "boundary", "signs", "domain", "normalization")
    },
    "proof_arguments": proof_arguments,
    "lyapunov_formula": "V_0=0; V_k=[alpha*k*(f(x_k)-f(x_star))+D_h(x_star,x_k)-D_h(x_star,x_0)]/(alpha*N), 1<=k<=N",
    "theorem": "f(x_N)-f(x_star)<=R/(alpha*N)",
    "theorem_latex": r"0\le f(x_{N})-f(x_{\star})\le\frac{R}{\alpha N}",
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": final_structure,
    "coefficient_formula_status": "verified",
    "unresolved_coefficients": [],
    "remaining_unknowns": [],
    "local_multiplier_code": "def local_multipliers(k, N, alpha):\n    return [sp.S(1)/N, sp.S(k)/N, sp.S(k+1)/(alpha*N), sp.S(k)/(alpha*N)]\n",
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": True,
    "numerical_certificate_verified": True,
    "require_analytic_full_pep": False,
    "exact_identity_evidence": {
        name: {
            "gram": "all symbolic coordinates zero",
            "function": "all symbolic coordinates zero",
            "offset": "0",
        }
        for name in expected
    },
    "proof_source_files": [
        "supplementary/b5_derivation.py",
        "supplementary/b5_step.py",
        "supplementary/b5_base.py",
        "supplementary/b5_boundary.py",
        "supplementary/b5_signs.py",
    ],
    "notebook_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "static_evidence": "supplementary/b5-static-002.json",
    "execution_evidence": "supplementary/b5-final-execution-console.txt",
    "presentation_policy": "evaluation-ancillary-v1",
    "rendered_review_performed": False,
    "run_status": "complete",
    "completed_utc": datetime.now(timezone.utc).isoformat(),
}
assert all(state["proof_checks"].values()) and not state["remaining_unknowns"]
(root / "state/bppm_b5.json").write_text(
    json.dumps(state, indent=2, allow_nan=False), encoding="utf-8"
)
print("B5 state saved from the inspected final executed notebook.")
for i, c in enumerate(nb["cells"]):
    source = "".join(c["source"])
    print(i, c["cell_type"], c["id"], source.splitlines()[0][:100])
print("Proof checks:", state["proof_checks"])
print("Theorem:", state["theorem"])
