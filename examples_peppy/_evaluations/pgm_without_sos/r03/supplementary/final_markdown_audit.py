import json
import re
from pathlib import Path
root=Path.cwd()
p=root/'pgm_example_lyap.ipynb'
b=json.loads(p.read_text())
for c in b['cells']:
    if c['cell_type']=='markdown':
        s=''.join(c['source'])
        lines=s.splitlines(keepends=True)
        for i,line in enumerate(lines):
            stripped=line.rstrip('\n')
            if stripped.endswith('\\') and not stripped.endswith('\\\\'):
                lines[i]=stripped+'\\'+ ('\n' if line.endswith('\n') else '')
        s=''.join(lines)
        s=s.replace('_\\star','_{\\star}')
        s=re.sub(r'_([A-Za-z0-9])(?![A-Za-z0-9])',r'_{\1}',s)
        s=s.replace('The ten independent symmetric coefficients remain analytic unknowns.','At the B4 handoff, the ten independent symmetric coefficients were analytic unknowns; the B5 finite-product derivation below resolves them.')
        s=s.replace('B5 must derive the remaining coefficients and prove the exact step, initial, and terminal identities; numerical reconstruction is not an analytic theorem.','The following B5 sections derive these coefficients and prove the exact step, initial, and terminal identities. This earlier numerical reconstruction alone was not an analytic theorem.')
        assert not any(ord(x)<32 and x not in '\n\t' for x in s)
        assert '\\(' not in s and '\\[' not in s
        c['source']=s.splitlines(keepends=True)
p.write_text(json.dumps(b,indent=1))
for index in (2,3):
    for line in ''.join(b['cells'][index]['source']).splitlines():
        if line.endswith('\\'):
            assert len(line)-len(line.rstrip('\\'))==2
print('Final Markdown equation-source audit passed; matrix/aligned row breaks repaired without changing executable cells.')
