import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat
import hashlib
root=runtime.ROOT
path=root/'feg_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
for cell in nb.cells:
    if cell.source.startswith('## Partial-sum'):
        cell.source=r'''## Partial-sum Lyapunov construction and rank profile
Initial B3 exploration at $N=4$ used the consecutive monotonicity and half-step Lipschitz residuals, leaving the terminal zero-point monotonicity term and the full PSD remainder for the boundary argument. All Gram, function and offset coverage checks passed. The ranks are $[0,2,2,2,2]$ at absolute tolerance $10^{-4}$, with no singular values near the threshold. Excluding $V_0,V_N$ leaves three rank-two terms.
Cross-horizon confirmation is pending a coherent $N=6$ certificate acquired in B2. This is incomplete B3 evidence, not a completed rank-search gate.'''
nbformat.write(nb,path)
check=root/'supplementary/feg_example_lyap_checklist.md'
text=check.read_text()
lines=text.splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'): lines[i]='Last reviewed block: B3 initial exploration (incomplete)'
    if line.startswith('SHA-256:'): lines[i]='SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()
check.write_text('\n'.join(lines)+'\n')
