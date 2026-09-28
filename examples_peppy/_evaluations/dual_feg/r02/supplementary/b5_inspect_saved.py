import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
nb=json.loads((root/'dual_feg_example_lyap.ipynb').read_text(encoding='utf-8'))
for i,c in enumerate(nb['cells']):
    source=''.join(c['source'])
    outputs=c.get('outputs',[])
    texts=[''.join(o.get('text',[])) for o in outputs if o['output_type']=='stream']
    print(i,c['cell_type'],source.splitlines()[0][:85], 'exec',c.get('execution_count'), 'outputs',len(outputs))
    if i>=34:
        for t in texts:
            print(t[:2000])
