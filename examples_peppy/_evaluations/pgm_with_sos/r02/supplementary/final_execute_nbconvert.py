import importlib.util
import os
import runpy
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',root/'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
sys.argv=['jupyter-nbconvert','--to','notebook','--execute',str(root/'pgm_example_lyap.ipynb'),'--output','pgm_example_lyap.ipynb','--output-dir',str(root),'--ExecutePreprocessor.timeout=180','--ExecutePreprocessor.kernel_name=pgm-own']
print('Executing nbconvert:',sys.argv,flush=True)
runpy.run_module('nbconvert',run_name='__main__')
