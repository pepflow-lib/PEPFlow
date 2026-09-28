from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import subprocess
import json
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
os.environ['JUPYTER_NO_CONFIG']='1'
command=[sys.executable,'-I','-B','-m','nbconvert','--to','notebook','--execute',str(runtime.ATTEMPT/'pgm_example_lyap.ipynb'),
         '--output','pgm_example_lyap.ipynb','--output-dir',str(runtime.ATTEMPT),
         '--ExecutePreprocessor.kernel_name=pgm-attempt','--ExecutePreprocessor.timeout=180']
result=subprocess.run(command,cwd=runtime.ATTEMPT,check=False)
(runtime.ATTEMPT/'supplementary/b5-final-execution.json').write_text(json.dumps({'command':command,'returncode':result.returncode,'cwd':str(runtime.ATTEMPT),'kernel':'pinned python -I -B','presentation_policy':'evaluation-ancillary-v1'},indent=2))
raise SystemExit(result.returncode)
