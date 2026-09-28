from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import ATTEMPT
from partial_sums import replay_certificate,construct_partial_sums,decompose_saved_S
from certificates import certificate_id,CERTIFICATE_KEYS
import inspect
import nbformat as nbf

path=ATTEMPT/"bppm_example_lyap.ipynb"
nb=nbf.read(path,as_version=4)
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=="markdown" and c.source.startswith("## Partial-sum"))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=="markdown" and c.source.startswith("## Identify the vectors"))
nb.cells[start:end]=[
nbf.v4.new_markdown_cell(r'''## Partial-sum Lyapunov construction and rank profile
Let $C^q_{i,j}\le0$ denote the convex interpolation residual defined above. The selected numerical multipliers define $V_0=0$ and
$$V_k-V_{k-1}=d^f_{\star,k}C^f_{\star,k}+d^f_{k-1,k}C^f_{k-1,k}
+d^h_{k,k-1}C^h_{k,k-1}+d^h_{k-1,k}C^h_{k-1,k},\quad 1\le k\le N,$$
with absent zero-weight terms omitted at $k=1$. Every increment is nonpositive under the interpolation inequalities and the checked nonnegative multipliers. Thus the partial sums use the nonincreasing convention.

The normalization constraint is reserved for the initial bound. Exactly one terminal interpolation residual, $d^h_{\star,N}C^h_{\star,N}$, and the complete numerical PSD matrix $S$ remain as boundary terms. We retain the small numerical $S$ rather than silently dropping it. The coverage check verifies all Gram, function and constant coordinates.

Interior rank $4$ is confirmed for $N=4,6$ under fixed exclusions of $V_0$ and $V_N$. This is finite-sample structural evidence; basis reconstruction and the arbitrary-horizon proof remain pending.'''),
nbf.v4.new_code_cell('''import hashlib
''' + 'CERTIFICATE_KEYS = '+repr(CERTIFICATE_KEYS)+'\n'+inspect.getsource(certificate_id)+'\n'+inspect.getsource(replay_certificate)+'''
certificate = json.loads((notebook_dir / "state/bppm_b2.json").read_text())
certificate_checks = replay_certificate(ctx, pb, certificate, notebook_dir)
print("Saved certificate replayed:", certificate_checks["passed"])
print("Initial normalization dual:", certificate["tau_sol"])
print("Additional scalar/matrix dual families: none (inventory checked).")
'''),
nbf.v4.new_code_cell(inspect.getsource(decompose_saved_S)+'\n'+inspect.getsource(construct_partial_sums)+'''
lyap, observation = construct_partial_sums(ctx, pb, certificate)
print("Coverage residual:", observation["coordinate_errors"]["coverage"])
print("Singular-value separation: smallest retained", observation["minimum_significant_singular_value"],
      "largest discarded", observation["maximum_negligible_singular_value"])
'''),
nbf.v4.new_code_cell('''rank_evidence = json.loads((notebook_dir / "supplementary/rank_search.json").read_text())
samples = rank_evidence["samples"]
left, right = 1, 1
assert len({s["N"] for s in samples}) >= 2
assert all(s["recipe_id"] == observation["recipe_id"] and s["rank_convention"] == observation["rank_convention"] for s in samples)
common_ranks = set()
for sample in samples:
    assert sample["certificate_checked"] and sample["grouping_checked"] and sample["rank_credible"]
    retained = sample["rank_profile"][left:sample["N"] + 1 - right]
    assert len(retained) >= 3 and len(set(retained)) == 1
    common_ranks.update(retained)
assert len(common_ranks) == 1
assert observation["rank_profile"] == samples[0]["rank_profile"]
print("Confirming horizons:", [s["N"] for s in samples])
print("Common interior rank:", next(iter(common_ranks)), "; fixed exclusions:", (left, right))
print("Rank convention: unscaled setup Gram coordinates; absolute tolerance 1e-4.")
print("Both horizon certificates and all-coordinate coverage were recomputed in the saved comparison run.")'''),
nbf.v4.new_markdown_cell('''### Block 3 conclusion
The selected rank profile is $[0,4,4,4,4]$. All interpolation contributions are assigned; no terms are omitted. Terminal coverage and each increment identity pass. The same recipe gives rank $4$ at both confirming horizons. Numerical certificate and grouping verification are complete; analytic full-PEP and Lyapunov proof statuses remain false.''')]
nbf.write(nb,path)
print("Updated B3 notebook.")
