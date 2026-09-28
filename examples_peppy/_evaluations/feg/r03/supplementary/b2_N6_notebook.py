import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat
import hashlib
import json
root=runtime.ROOT
path=root/'feg_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
sample=json.loads((root/'supplementary/b2-N6.json').read_text())
index=next(i for i,c in enumerate(nb.cells) if c.source.startswith('## Partial-sum'))
nb.cells.insert(index,nbformat.v4.new_markdown_cell(r'''### Additional B2 certificate for cross-horizon exploration
The same sparse support recipe was solved at $N=6$, preserving the dense bound within $7.46\times10^{-10}$. The complete saved certificate has maximum identity residual $7.52\times10^{-9}$ and remainder reconstruction residual $4.45\times10^{-16}$. Its provenance and all constraints are in `supplementary/b2-N6.json`.
The proposed lambda and S formulas differ from this numerical optimizer by approximately $7.64\times10^{-4}$ and $4.58\times10^{-4}$, respectively, exceeding the fixed $10^{-4}$ comparison tolerance. They remain unresolved for this sample; the verified numerical values are retained without substitution. The selected main certificate remains $N=4$.'''))
nbformat.write(nb,path)
check=root/'supplementary/feg_example_lyap_checklist.md'
lines=check.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'):lines[i]='Last reviewed block: B2 N6 acquisition'
    if line.startswith('SHA-256:'):lines[i]='SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()
    for item,heading in [(9,'## Partial-sum'),(10,'## Identify'),(11,'## Coefficient'),(12,'## Symbolic')]:
        if line.startswith(f'| {item} |'):
            parts=line.split('|');parts[4]=' '+str(next(j for j,c in enumerate(nb.cells) if c.source.startswith(heading)))+' ';lines[i]='|'.join(parts)
check.write_text('\n'.join(lines)+'\n')
