import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
from pgm_setup import get_pep_setup,f,g
notebook_dir=runtime.ROOT
b3=json.loads((notebook_dir/'state/pgm_b3.json').read_text())
certificate=b3
for field in ['certificate_check_code','decomposition_code','grouping_code']:
    exec(compile(b3[field],field,'exec'))
assert ranks==b3['rank_profile']
assert b3['rank_search']['status']=='confirmed'
assert json.loads((notebook_dir/b3['rank_search']['evidence_path']).read_text())['summary']==b3['rank_search']
for k,Vk in enumerate(lyap):
    value=pm.eval_scalar(Vk)
    for actual,saved in [(value.inner_prod_coords,b3['lyap_inner_prod_coords'][k]),(value.func_coords,b3['lyap_func_coords'][k]),(value.offset,b3['lyap_offsets'][k])]:
        assert np.allclose(np.asarray(actual,dtype=float),np.asarray(saved,dtype=float),atol=1e-4,rtol=1e-5)
exec(compile((notebook_dir/'supplementary/b4_notebook_cells.py').read_text(encoding='utf-8-sig'),'b4_cells','exec'))
