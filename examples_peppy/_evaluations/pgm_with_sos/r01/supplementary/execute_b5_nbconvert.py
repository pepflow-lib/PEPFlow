import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import subprocess
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
args=[sys.executable,'-I','-B','-m','nbconvert','--to','notebook','--execute','pgm_example_lyap.ipynb','--output','pgm_example_lyap.ipynb','--output-dir',str(runtime.ATTEMPT),'--ExecutePreprocessor.kernel_name=pgm-attempt','--ExecutePreprocessor.timeout=180']
print('Executing:',args,flush=True)
result=subprocess.run(args,cwd=runtime.ATTEMPT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
(runtime.ATTEMPT/'supplementary/b5-nbconvert-001-output.txt').write_text(result.stdout)
print(result.stdout)
raise SystemExit(result.returncode)
