from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import ATTEMPT,RUNTIME
import os
import json
import subprocess
import nbformat

os.environ["JUPYTER_PATH"]=str(RUNTIME/"jupyter")
path=ATTEMPT/"bppm_example_lyap.ipynb"
nb=nbformat.read(path,as_version=4)
for c in nb.cells:
    if c.cell_type=="markdown":
        assert not any(char in c.source for char in ('\x0c','\r','\x08'))
        assert '\\(' not in c.source and '\\[' not in c.source
command=[sys.executable,"-I","-B","-m","jupyter","nbconvert","--to","notebook","--execute",str(path),
         "--output",path.name,"--output-dir",str(ATTEMPT),"--ExecutePreprocessor.kernel_name=bppm-r02","--ExecutePreprocessor.timeout=120"]
result=subprocess.run(command,cwd=ATTEMPT,capture_output=True,text=True,timeout=180)
record={"command":command,"cwd":str(ATTEMPT),"returncode":result.returncode,"stdout":result.stdout,"stderr":result.stderr}
(ATTEMPT/"supplementary/b5-nbconvert-execution.json").write_text(json.dumps(record,indent=2))
print(result.stdout)
print(result.stderr)
assert result.returncode==0
nb=nbformat.read(path,as_version=4)
summary=[]
for i,c in enumerate(nb.cells):
    if c.cell_type=="code":
        assert c.execution_count is not None
        assert not any(o.output_type=="error" for o in c.outputs)
        summary.append({"cell":i,"execution_count":c.execution_count,"output_types":[o.output_type for o in c.outputs],
                        "text":[o.get("text","") for o in c.outputs if o.output_type=="stream"],
                        "has_plot":any("image/png" in o.get("data",{}) for o in c.outputs)})
(ATTEMPT/"supplementary/b5-notebook-execution.json").write_text(json.dumps(summary,indent=2))
print("Final notebook clean-kernel nbconvert execution passed.")
