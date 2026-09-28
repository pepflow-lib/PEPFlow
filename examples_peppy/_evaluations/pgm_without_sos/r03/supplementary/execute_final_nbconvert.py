import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import os
import sys
root=Path.cwd()
os.environ['JUPYTER_PATH']=str(root/'supplementary/.runtime/jupyter')
sys.argv=['nbconvert','--to','notebook','--execute',str(root/'pgm_example_lyap.ipynb'),'--inplace','--ExecutePreprocessor.kernel_name=pgm-own','--ExecutePreprocessor.timeout=180']
runpy.run_module('nbconvert',run_name='__main__')
