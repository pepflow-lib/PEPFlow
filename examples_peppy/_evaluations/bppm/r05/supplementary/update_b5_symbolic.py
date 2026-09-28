"""Refresh exact-proof source cells after the symbolic API typing adaptation."""
from pathlib import Path
import nbformat as nbf

root=Path(__file__).resolve().parents[1]
nbpath=root/'bppm_example_lyap.ipynb'
nb=nbf.read(nbpath,as_version=4)
for name in ('symbolic_common','step','base','boundary'):
    source=(root/f'supplementary/b5_{name}.py').read_text()
    prefix=source.splitlines()[0]
    matches=[c for c in nb.cells if c.cell_type=='code' and c.source.startswith(prefix)]
    assert len(matches)==1
    matches[0].source=source
nbf.write(nb,nbpath)
