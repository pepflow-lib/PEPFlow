import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import textwrap
import nbformat
root=Path.cwd()
check=(root/'supplementary/certificate_check.py').read_text(encoding='utf-8-sig')
decomp=(root/'supplementary/decomposition_b3.py').read_text(encoding='utf-8-sig')
group=(root/'supplementary/grouping_b3.py').read_text(encoding='utf-8-sig')
init='''import sympy as sp
import pepflow as pf
N_int=certificate['N_verify']
params_sp: dict[str, pf.NUMERICAL_TYPE]={'L':sp.Integer(1),'R':sp.Integer(1)}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
'''
function='def reconstruct_and_group(certificate):\n'+textwrap.indent(init+check+'\n'+decomp+'\n'+group+'\nreturn locals()\n','    ')
tail='''
certificates=[json.loads((NOTEBOOK_DIR/path).read_text()) for path in ('state/pgm_b2.json','supplementary/pgm_b2_N6.json')]
samples=[reconstruct_and_group(cert) for cert in certificates]
assert len({sample['N_int'] for sample in samples})==2
for sample in samples:
    retained=sample['ranks'][1:sample['N_int']]
    assert len(retained)>=3 and set(retained)=={4}
    assert sample['certificate_checked'] and sample['grouping_checked']
    for k in range(1,sample['N_int']):
        assert not any(1e-5<v<1e-3 for v in sample['singular_values'][k])
print('Cross-horizon interior rank confirmed: 4 at N=4 and N=6; exclude V_0 and V_N; absolute tolerance 1e-4, no coordinate scaling.')
selected_sample=samples[0]
'''
source=function+tail
(root/'supplementary/b3_visible.py').write_text(source)
book=nbformat.read(root/'pgm_example_lyap.ipynb',as_version=4)
b3_start=next(i for i,c in enumerate(book.cells) if c.cell_type=='markdown' and c.source.startswith('## B3'))
b4_start=next(i for i,c in enumerate(book.cells) if c.cell_type=='markdown' and c.source.startswith('## B4'))
book.cells[b3_start:b4_start]=[nbformat.v4.new_markdown_cell(r'''## B3 partial sums and cross-horizon rank
For each normalized interpolation residual $R_c\le0$, let $d_c\ge0$ be its selected multiplier. Reverse LDL decomposes the same numerical remainder into PSD pieces $Q_j$. The step assignment uses the latest iterate gradient in each factor; initial factors and the $(\star,0)$ term are included in the first increment.
$$V_0=0,\qquad V_{k+1}-V_k=\sum_{c\in A_k}d_cR_c-\sum_{j\in B_k}Q_j\le0.$$
All interpolation terms and all remainder pieces are included. The initial-condition term remains in the terminal boundary identity. This numerical construction gives interior rank four at $N=4$ and $N=6$, with fixed exclusions $V_0,V_N$. Rank is computed in the original coordinates at absolute tolerance $10^{-4}$ without scaling. All retained singular values are separated from the threshold. The terminal quadratic rank is one, consistent with the initial squared-distance boundary. Rank evidence alone does not prove a common basis or an all-horizon theorem.
'''),nbformat.v4.new_code_cell(source)]
nbformat.write(book,root/'pgm_example_lyap.ipynb')


