import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "supplementary/b5_initialize.py"
s = p.read_text(encoding="utf-8-sig").replace(
    "resolve_parameters=exact_parameters",
    "resolve_parameters=cast(dict[str, pf.NUMERICAL_TYPE], exact_parameters)",
)
p.write_text(s)
p = root / "bppm_example_lyap.ipynb"
nb = json.loads(p.read_text())
for c in nb["cells"]:
    s = "".join(c["source"])
    if c["cell_type"] == "code" and s.startswith("import sympy as sp\n\nb4 ="):
        s = (root / "supplementary/b5_initialize.py").read_text()
    if c["cell_type"] == "markdown" and s.startswith("### Theorem"):
        s = s.replace(
            "Under the stated assumptions, for every integer",
            r"Let $f,h$ be closed, proper, convex and differentiable as specified, on a real finite-dimensional Euclidean space. Let $x_{\star}$ minimize $f$, let $\alpha>0$, $R\ge0$, and assume $D_h(x_{\star},x_{0})\le R$. Suppose every update $x_{k+1}\in\arg\min_x\{\alpha f(x)+D_h(x,x_{k})\}$ and stated evaluation exists. Then for every integer",
        )
    if c["cell_type"] == "markdown" and s.startswith(
        "## Closed form and exact identities"
    ):
        s += r"""
The resolved closed form is
$$V_{k}=\frac{D_h(x_{\star},x_{k})-D_h(x_{\star},x_{0})}{\alpha N}+\frac{k}{N}(f(x_{k})-f(x_{\star})),\qquad 0\le k\le N.$$
The next cells verify its one-step identity, including every function-value term."""
    c["source"] = s.splitlines(keepends=True)
p.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
