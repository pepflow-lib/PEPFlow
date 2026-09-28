import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'dual_feg_example_lyap.ipynb'
nb=json.loads(p.read_text())
for c in nb['cells']:
    if c['cell_type']=='code':
        s=''.join(c['source'])
        if "print('Selected S eigenvalues:'" in s:
            s=s.replace("print('Selected S eigenvalues:',np.linalg.eigvalsh(S_array))", "print('Selected S eigenvalues:',np.linalg.eigvalsh(S_array))\nprint('Labeled numerical Gram remainder from the selected solve:')\npf.pprint_labeled_matrix(S_named)")
        c['source']=s
p.write_text(json.dumps(nb,indent=1))
