import json
import re
from pathlib import Path
b=json.loads(Path('pgm_example_lyap.ipynb').read_text())
for i,c in enumerate(b['cells']):
    if c['cell_type']=='markdown':
        s=''.join(c['source'])
        print(i,s.splitlines()[0])
        doubled=re.findall(r'\\\\[A-Za-z]+',s)
        if doubled:
            print('SUSPICIOUS_DOUBLE_COMMAND',doubled[:8])
print('Theorem prefix repr:',repr(''.join(b['cells'][2]['source'])[:140]))
print('Theorem matrix repr:',repr(''.join(b['cells'][2]['source']).split('pmatrix')[1][:180]))
