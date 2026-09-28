import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import subprocess
root=runtime.ROOT
command=[sys.executable,'-I','-B','-m','jupyter','nbconvert','--to','notebook','--execute',str(root/'feg_example_lyap.ipynb'),'--output','feg_example_lyap.ipynb','--output-dir',str(root),'--ExecutePreprocessor.kernel_name=feg-private','--ExecutePreprocessor.timeout=120']
result=subprocess.run(command,cwd=root,capture_output=True,text=True)
(root/'supplementary/b5-final-execution.json').write_text(json.dumps(dict(command=command,cwd=str(root),returncode=result.returncode,stdout=result.stdout,stderr=result.stderr),indent=2))
print(result.stdout)
print(result.stderr)
raise SystemExit(result.returncode)
