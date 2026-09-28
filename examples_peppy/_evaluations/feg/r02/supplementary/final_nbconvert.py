import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import os
import sys
root=Path(__file__).resolve().parents[1]
os.environ['JUPYTER_PATH']=str(root/'supplementary/.runtime/jupyter')
sys.argv=['jupyter-nbconvert','--to','notebook','--execute',str(root/'feg_example_lyap.ipynb'),'--ExecutePreprocessor.kernel_name=feg-owned','--ExecutePreprocessor.timeout=120','--output','feg_example_lyap.ipynb','--output-dir',str(root)]
runpy.run_module('nbconvert',run_name='__main__')
