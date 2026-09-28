import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'feg_example_lyap.ipynb'
nb=json.loads(p.read_text(encoding='utf-8'))
old="pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(exact_coefficients(k_symbol,N_symbol,L_symbol),dtype=object),['A(x_k)','x_k-x_0'],['A(x_k)','x_k-x_0']))"
new="pf.pprint_labeled_matrix(np.asarray(exact_coefficients(k_symbol,N_symbol,L_symbol),dtype=object),['A(x_k)','x_k-x_0'],['A(x_k)','x_k-x_0'],precision=0)"
for c in nb['cells']:
    s=''.join(c['source'])
    if old in s:
        c['source']=s.replace(old,new)
p.write_text(json.dumps(nb,indent=1,ensure_ascii=False),encoding='utf-8')
p=root/'supplementary/b5_coefficients_cell.py'
p.write_text(p.read_text(encoding='utf-8-sig').replace(old,new),encoding='utf-8')
