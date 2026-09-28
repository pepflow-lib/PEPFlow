import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import nbformat as nbf
root=Path(__file__).resolve().parents[1]
p=root/'feg_example_lyap.ipynb'
nb=nbf.read(p,as_version=4)
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Lyapunov partial sums'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Identify the vectors'))
check=(root/'supplementary/b3_certificate_check.py').read_text(encoding='utf-8-sig').replace('from pepflow.constraint import ScalarConstraint, PSDConstraint','from pepflow.constraint import ScalarConstraint')
nb.cells[start:end]=[nbf.v4.new_markdown_cell(r'''## Lyapunov partial sums and rank profile
Define $\operatorname{Mon}(u,v)=-\langle A(u)-A(v),u-v\rangle\le0$ and $\operatorname{Lip}(u,v)=\|A(u)-A(v)\|^2-L^2\|u-v\|^2\le0$. Using the selected numerical nonnegative multipliers $m_k,\ell_k$, set $V_0=0$ and
$$V_{k+1}-V_k=\ell_k\operatorname{Lip}(x_{k+1/2},x_{k+1})+\mathbf{1}_{k\ge1}m_k\operatorname{Mon}(x_k,x_{k+1}).$$
Thus the numerical construction has the nonincreasing sign convention. The terminal root monotonicity contribution and the entire PSD matrix $S$ remain boundary terms. No interpolation contribution is omitted. The initial-condition normalization is handled separately by the final bound.

The same construction has rank two for all nonzero indices at horizons 6 and 8. The formal comparison excludes $V_0,V_N$ at each horizon and uses absolute tolerance $10^{-4}$ in the original Gram coordinates at $L=R=1$. This is numerical discovery evidence, not an arbitrary-horizon proof.'''),nbf.v4.new_code_cell('certificate = json.loads((notebook_dir / "state/feg_b2.json").read_text())\nREPO_ROOT = repo_root\nN_int = certificate["N_verify"]\nparams_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.Integer(1), "R": sp.Integer(1)}\nctx, pb, obj = get_pep_setup(N_int, params_sp)\npb.set_relaxed_constraints(certificate["relaxed_constraints"])\nctx.set_as_current()'),nbf.v4.new_code_cell(check),nbf.v4.new_code_cell((root/'supplementary/b3_decomposition.py').read_text(encoding='utf-8-sig')),nbf.v4.new_code_cell((root/'supplementary/b3_grouping.py').read_text(encoding='utf-8-sig')),nbf.v4.new_code_cell('rank_evidence = json.loads((notebook_dir / "supplementary/rank_search.json").read_text())\nsummary = rank_evidence["summary"]\nprint("Confirmed horizons:", summary["confirmed_horizons"], "common rank:", summary["rank"])\nprint("Fixed boundary exclusions:", summary["boundary_exclusions"], "rank tolerance:", rank_tolerance)\nfor sample in rank_evidence["samples"]:\n    retained = sample["rank_profile"][1:-1]\n    assert len(retained)>=3 and set(retained)=={2}\n    spectra = sample["singular_values"][1:-1]\n    print("N =",sample["N"], "smallest retained singular value =",min(s[1] for s in spectra),"largest discarded =", max(s[2] for s in spectra))'),nbf.v4.new_markdown_cell('### Block 3 conclusion\nThe selected profile is $[0,2,2,2,2,2,2]$. Both horizons pass full-coordinate certificate, decomposition, step-increment, and coverage checks. Boundary leftovers are one root monotonicity term and one complete PSD piece. Exact formulas and their analytic signs remain obligations for the later proof.')]
nbf.write(nb,p)

