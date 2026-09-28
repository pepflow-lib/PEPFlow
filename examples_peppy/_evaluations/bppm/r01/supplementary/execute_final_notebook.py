import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import json
import runpy
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
notebook=runtime.ROOT/'bppm_example_lyap.ipynb'
sys.argv=['jupyter-nbconvert','--to','notebook','--execute',str(notebook),'--output',notebook.name,'--output-dir',str(runtime.ROOT),'--ExecutePreprocessor.timeout=120','--ExecutePreprocessor.kernel_name=bppm-owned']
(runtime.ROOT/'supplementary/b5-final-execution-command.json').write_text(json.dumps({'python':sys.executable,'flags':['-I','-B'],'module':'nbconvert','argv':sys.argv,'cwd':str(Path.cwd()),'kernel':'bppm-owned','presentation_policy':'evaluation-ancillary-v1'},indent=2),encoding='utf-8')
runpy.run_module('nbconvert',run_name='__main__')
