"""Save verified numerical structure and author the B4 notebook section."""
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "supplementary"),str(ROOT / "supplementary/helpers")]
from b4_notebook_cells import SANITY,SCAN,FILTER,SEARCH,BASIS,EXTRACT,FIT  # noqa: E402
from notebook_runtime import execute_notebook  # noqa: E402
import nbformat as nbf  # noqa: E402

b3 = json.loads((ROOT / "state/ogm_b3.json").read_text())
data = json.loads((ROOT / "supplementary/b4-exploration.json").read_text())
basis_code = BASIS[:BASIS.index("for k in range(N+1):")]
structure_function = EXTRACT[EXTRACT.index("def V_k_structure(k):"):EXTRACT.index("for k in range(N+1):",EXTRACT.index("def V_k_structure(k):"))]
structure_code = "alpha_by_k = "+repr({int(k):v for k,v in data["alpha_by_k"].items()})+"\n"+structure_function
coeff_code = FIT[:FIT.index("formula_residuals = {}")]
structure: dict[str,Any] = dict(quadratic_convention="sum_ij C_ij <v_i,v_j>; symmetric C, off-diagonal entries count twice",
    initial=dict(index_domain="k=0",basis_labels=[],coefficients={}),
    interior=dict(index_domain="1 <= k <= N-1",basis_labels=["x_0-x_star","z_{k+1}-x_star","g_k"],
                  coefficients={"C00":"-L/(2*theta_N**2)","C11":"L/(2*theta_N**2)","C22":"-theta_k**2/(L*theta_N**2)","C01":"0","C02":"0","C12":"0"}),
    terminal=dict(index_domain="k=N",basis_labels=["x_0-x_star","z_N-x_star-theta_N*g_N/L"],
                  coefficients={"C00":"-L/(2*theta_N**2)","C11":"L/(2*theta_N**2)","C01":"0"}),
    function_terms=[dict(expression="f(x_k)-f(x_star)",index_domain="1 <= k <= N-1",coefficient="2*theta_k**2/theta_N**2"),
                    dict(expression="f(x_N)-f(x_star)",index_domain="k=N",coefficient="1")],constant_terms=[])
b4 = {**b3,"basis_templates":{"initial":[],"interior":structure["interior"]["basis_labels"],"terminal":structure["terminal"]["basis_labels"]},
      "basis_code":basis_code,"structure_code":structure_code,"coeff_by_k":data["coeff_by_k"],
      "coeff_code":coeff_code,"coefficient_formula_status":"candidate","expression_structure":structure,
      "unresolved_coefficients":[],"formula_residuals":data["formula_residuals"],
      "numerical_reconstruction":dict(certificate_id=b3["certificate_id"],required_indices=list(range(b3["N_verify"]+1)),
          quadratic_residuals=data["quadratic_residuals"],component_residuals=data["component_residuals"],
          tolerances=dict(indep_tol=1e-7,span_tol=1e-5,component_atol=1e-4,component_rtol=1e-5),passed=True),
      "analytic_full_pep_verified":False,"lyapunov_proof_verified":False}
(ROOT / "state/ogm_b4.json").write_text(json.dumps(b4,indent=2,allow_nan=False))

pattern = r'''### Selected basis pattern
The exhaustive sparse search selected the following interpretable basis, in this order:
$$\mathcal B_k=[x_0-x_\star,\ z_{k+1}-x_\star,\ g_k]\quad(1\le k<N).$$
For $k=N$, use $\mathcal B_N=[x_0-x_\star,q_N]$, where $q_N=z_N-x_\star-\theta_Ng_N/L$.
The zero base $V_0$ uses the empty basis. The terminal vector comes from the Block 2 remainder candidate; $z_{k+1}$ is already an algorithm variable.
'''
conclusion = r'''### Block 4 conclusion
Write $T=\theta_N$ and $d_0=x_0-x_\star$. The numerical reconstruction suggests $V_0=0$ and
$$V_k=\frac{L}{2T^2}\bigl(\|z_{k+1}-x_\star\|^2-\|d_0\|^2\bigr)
-\frac{\theta_k^2}{LT^2}\|g_k\|^2+\frac{2\theta_k^2}{T^2}\bigl(f(x_k)-f(x_\star)\bigr),\quad 1\le k<N,$$
$$V_N=f(x_N)-f(x_\star)+\frac{L}{2T^2}\bigl(\|q_N\|^2-\|d_0\|^2\bigr).$$
There are no constant terms. Every sample index, including the empty initial basis and the terminal basis, passed independence and full-expression reconstruction. These formulas are candidates supported by the selected numerical sample; Block 5 must prove their exact step, initial, and terminal identities for arbitrary horizons. No analytic full-PEP or Lyapunov proof is claimed here.
'''
path = ROOT / "ogm_example_lyap.ipynb"
nb = nbf.read(path,as_version=4)
start = next(i for i,c in enumerate(nb.cells) if c.id in ("b4-placeholder","b4-heading"))
end = next(i for i,c in enumerate(nb.cells) if c.id == "b5-placeholder")
nb.cells[start:end] = [
    nbf.v4.new_markdown_cell("## Identify the vectors composing the Lyapunov function\nStarting from the rechecked B3 partial sums, search for independent, interpretable vectors spanning each quadratic matrix.",id="b4-heading"),
    nbf.v4.new_code_cell(SANITY,id="b4-sanity"),
    nbf.v4.new_markdown_cell("### Candidate-vector scan\nCandidates include tagged x/y/z iterates, gradients, point-to-solution gaps, pairwise differences, the initial anchor, and the terminal remainder vector. Deduplicate by numerical coordinates and omit zero vectors.",id="b4-scan-heading"),
    nbf.v4.new_code_cell(SCAN,id="b4-candidate-build"),
    nbf.v4.new_code_cell(FILTER,id="b4-candidate-filter"),
    nbf.v4.new_markdown_cell(pattern,id="b4-basis-heading"),
    nbf.v4.new_code_cell(SEARCH,id="b4-search"),
    nbf.v4.new_code_cell(BASIS,id="b4-basis"),
    nbf.v4.new_markdown_cell("### Coefficient matrices\nUse the basis order above and the symmetric quadratic convention, counting off-diagonal entries twice. Function gaps and scalar offsets are checked separately; no coordinate family is discarded.",id="b4-coeff-heading"),
    nbf.v4.new_code_cell(EXTRACT,id="b4-extract"),
    nbf.v4.new_code_cell(FIT,id="b4-fit"),
    nbf.v4.new_markdown_cell(conclusion,id="b4-conclusion")]
nbf.write(nb,path)
execute_notebook(path,"b4")
