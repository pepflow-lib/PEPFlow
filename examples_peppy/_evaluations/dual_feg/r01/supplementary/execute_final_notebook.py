import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import json
import subprocess
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
command=[sys.executable,'-I','-B','-m','nbconvert','--to','notebook','--execute',str(runtime.ATTEMPT/'dual_feg_example_lyap.ipynb'),'--inplace','--ExecutePreprocessor.kernel_name=dual-feg-attempt','--ExecutePreprocessor.timeout=120']
record={'command':command,'cwd':str(runtime.ATTEMPT),'runtime_root':str(runtime.RUNTIME)}
result=subprocess.run(command,cwd=runtime.ATTEMPT,env=os.environ.copy(),capture_output=True,text=True,timeout=300)
record.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
(runtime.ATTEMPT/'supplementary/b5-final-execution-002.json').write_text(json.dumps(record,indent=2))
print(result.stdout)
print(result.stderr)
raise SystemExit(result.returncode)

