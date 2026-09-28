from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / 'helpers'))
import runtime
import os
import nbformat
from nbclient import NotebookClient
os.environ['JUPYTER_PATH'] = str(runtime.RUNTIME / 'jupyter')
path = runtime.ATTEMPT / 'pgm_example_lyap.ipynb'
nb = nbformat.read(path, as_version=4)
NotebookClient(nb, timeout=180, kernel_name='pgm-attempt', resources={'metadata': {'path': str(runtime.ATTEMPT)}}).execute()
nbformat.write(nb, path)
for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'markdown':
        assert '\\(' not in cell.source and '\\[' not in cell.source
        assert not any(ord(c) < 32 and c not in '\n\t' for c in cell.source)
    for output in cell.get('outputs', []):
        assert output.output_type != 'error'
        if output.output_type == 'stream':
            print(i, output.text)
print('Fresh-kernel execution and source delimiter checks passed.')
