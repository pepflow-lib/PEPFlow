import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import nbformat as nbf
from nbclient import NotebookClient
root=runtime.ROOT
path=root/'bppm_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
md,code=nbf.v4.new_markdown_cell,nbf.v4.new_code_cell
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Lyapunov partial sums'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Special vectors'))
intro=md(r'''## Lyapunov partial sums and rank profile

For $I_q(u,v)=q(v)-q(u)+\langle\nabla q(v),u-v\rangle\le0$, group all consecutive edges by their larger iterate index. Starting from $V_0=0$, set
$$V_{k+1}-V_k=\widehat\lambda^f_{\star,k+1}I_f(x_\star,x_{k+1})+\widehat\lambda^f_{k,k+1}I_f(x_k,x_{k+1})+\widehat\lambda^h_{k+1,k}I_h(x_{k+1},x_k)+\widehat\lambda^h_{k,k+1}I_h(x_k,x_{k+1}).$$
The predecessor $f$ and forward $h$ terms with zero weight at $k=0$ are absent. All coefficients here are the actual saved numerical multipliers, and each increment is nonpositive under the interpolation inequalities.

The final identity leaves $\widehat\lambda^h_{\star,N}I_h(x_\star,x_N)$ and the full numerical Gram remainder $-S$ as boundary terms, along with the initial normalization inequality. No small numerical remainder is discarded. Thus the boundary signs agree with the nonincreasing convention.

The construction has quadratic rank 4 at both $N=4$ and $N=6$, using an absolute singular-value threshold $10^{-4}$ without rescaling. We exclude exactly $V_0$ and $V_N$ from the comparison, retaining three and five indices respectively. All endpoints remain covered by the identities. Rank confirmation is a finite-sample observation; basis reconstruction and an arbitrary-horizon proof remain for Blocks 4 and 5.''')
prelude=code('''REPO_ROOT = repo_root
SOURCE_ROOT = notebook_dir
certificate = json.loads((notebook_dir / "state/bppm_b2.json").read_text())
N_int = certificate["N_verify"]
params_sp = {"alpha": sp.S(1), "R": sp.S(1)}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
ctx.set_as_current()
''')
check=code((root/'supplementary/b3_certificate_check.py').read_text(encoding='utf-8-sig'))
group=code((root/'supplementary/b3_decomposition.py').read_text(encoding='utf-8-sig')+'\n'+(root/'supplementary/b3_grouping.py').read_text(encoding='utf-8-sig'))
coverage=code((root/'supplementary/b3_coverage.py').read_text(encoding='utf-8-sig'))
comparison=code((root/'supplementary/b3_assess.py').read_text()+'''\nrank_samples = [json.loads((notebook_dir / f"supplementary/b3-observation-N{n}.json").read_text()) for n in (4, 6)]
rank_search = assess_rank_pattern(rank_samples, certificate["certificate_id"], left=1, right=1)
assert rank_search["status"] == "confirmed"
assert rank_samples[0]["rank_profile"] == ranks
for sample in rank_samples:
    retained = sample["rank_profile"][1:sample["N"]]
    singular = sample["singular_values"]
    assert len(retained) >= 3 and set(retained) == {4}
    assert all(not any(1e-5 < s < 1e-3 for s in row) for row in singular)
    print(f"N={sample['N']}: {len(retained)} retained indices, common rank 4, full-coordinate coverage checked.")
print("Fixed boundary exclusions:", (1, 1), "; absolute rank tolerance:", rank_tolerance)
''')
nb.cells[start:end]=[intro,prelude,check,group,coverage,comparison]
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
nbf.write(nb,path)
NotebookClient(nb,timeout=120,kernel_name='bppm-owned',resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb,path)
for i,c in enumerate(nb.cells):
    if i>=start:
        for o in c.get('outputs',[]):
            if o.output_type=='stream':
                print(i,o.text)
print('B3 notebook fresh-kernel execution passed.')

