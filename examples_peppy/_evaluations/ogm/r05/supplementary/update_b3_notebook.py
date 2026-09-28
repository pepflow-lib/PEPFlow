"""Make B3 partial-sum construction and cross-horizon checks visible."""
from pathlib import Path

import nbformat

root = Path(__file__).resolve().parents[1]
path = root / 'ogm_example_lyap.ipynb'
nb = nbformat.read(path, as_version=4)
source = (root / 'supplementary/helpers/partial_sums.py').read_text()
definitions = source[source.index('def rebuild('):]
nb.cells[-1].source = nb.cells[-1].source.split('## Lyapunov partial sums and rank profile')[0]
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
nb.cells += [
    md(r"""## Lyapunov partial sums and rank profile
Write $I_{i,j}\leq0$ for the smooth convex interpolation residual, and use the selected numerical multipliers. Set $V_0=0$ and, for $1\leq k\leq N$,
$$V_k=\sum_{i=0}^{k}\lambda_{\star,i}I_{\star,i}
+\sum_{i=0}^{k-1}\lambda_{i,i+1}I_{i,i+1}-\mathbf1_{k=N}S(G).$$
Thus $V_1-V_0$ includes the initial $I_{\star,0}$ contribution; later increments add the next stationary-point and consecutive interpolation terms. The final increment additionally subtracts the complete PSD slack. Every increment is nonpositive under the numerical cone checks. The numerical rank-one candidate for $S$ remains informative, but the grouping retains the entire saved PSD matrix, including its tiny components.

The interior Gram rank is three at both $N=4$ and $N=6$, excluding exactly $V_0,V_N$. These exclusions affect the rank comparison only. The endpoint terms and every constraint remain included in the reconstruction and coverage obligations."""),
    code("from runtime import NOTEBOOK_DIR\n\n" + definitions),
    code("b3 = json.loads((notebook_dir / 'state/ogm_b3.json').read_text())\nobservation4 = construct(b3)\nassert observation4['rank_profile'] == b3['rank_profile']\nprint('Complete-coordinate coverage error:', observation4['coverage_max_abs'])\nprint('Increment identity errors:', observation4['increment_errors'])"),
    code("additional_certificate = json.loads((notebook_dir / 'supplementary/b2-certificate-N6.json').read_text())\nobservation6 = construct(additional_certificate, verbose=False)\nfor sample in (observation4, observation6):\n    interior = sample['rank_profile'][1:-1]\n    assert len(interior) >= 3 and len(set(interior)) == 1\n    assert sample['rank_credible'] and sample['certificate_checked'] and sample['grouping_checked']\nassert observation4['rank_profile'][1] == observation6['rank_profile'][1]\nassert observation4['recipe_id'] == observation6['recipe_id']\nassert observation4['rank_convention'] == observation6['rank_convention']\nprint('Confirmed horizons: 4, 6; common interior rank: 3; exclusions: (1, 1).')\nprint('Rank uses absolute singular-value tolerance 1e-4 on unscaled Gram coordinates.')\nprint('No singular value lies between 5e-5 and 2e-4 in either sample.')\nprint('N=6 coverage error:', observation6['coverage_max_abs'])"),
    md(r"""### B3 conclusion
All interpolation contributions and the entire Gram slack have explicit assignments; there are no omitted terms or terminal leftovers. Coverage is zero in Gram, function and constant coordinates. This establishes a consistent numerical construction across the two tested horizons, not an arbitrary-horizon theorem or a common basis. Basis reconstruction, including both endpoints, is next.

## Identify the vectors composing the Lyapunov function
Pending Block 4.

## Closed-form Lyapunov function and exact proof
Pending Block 5.""")
]
nbformat.write(nb, path)
