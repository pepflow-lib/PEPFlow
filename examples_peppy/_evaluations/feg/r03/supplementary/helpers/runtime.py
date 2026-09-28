"""Attempt-local runtime settings; no mathematical content."""
from pathlib import Path
import os
import sys
ROOT = Path(__file__).resolve().parents[2]
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
for key in ('TEMP','TMP','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR'):
    folder = ROOT / 'supplementary' / '.runtime' / key.lower()
    folder.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(folder)
os.environ['JUPYTER_PATH'] = str(ROOT / 'supplementary' / '.runtime' / 'jupyter')
sys.path[:0] = [str(ROOT/'supplementary'/'approved'), str(ROOT), str(ROOT/'supplementary'/'helpers')]
