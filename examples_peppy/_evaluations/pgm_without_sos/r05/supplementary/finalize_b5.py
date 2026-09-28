import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from owned_runtime import configure, ROOT
configure()
import json,os,subprocess
settings=json.loads((ROOT/'supplementary/approved/settings.json').read_text())
mode=sys.argv[1]
if mode=='static':
    argv=settings['preflight_command'][:-1]
    for flag,value in [('--evidence',str(ROOT/'supplementary/b5-static002.json')),('--helper-root',str(ROOT/'supplementary/helpers')),('--probe-helper-path','supplementary/helpers/runtime.py')]:argv[argv.index(flag)+1]=value
    argv+=['check','--','pgm_setup.py','pgm_example_lyap.ipynb','supplementary/helpers/solve_runtime.py']
else:
    os.environ['JUPYTER_PATH']=str(ROOT/'supplementary/.runtime/jupyter')
    os.environ['PATH']=str(Path(settings['python']).parent)+os.pathsep+os.environ['PATH']
    argv=[settings['python'],'-I','-B','-m','jupyter','nbconvert','--to','notebook','--execute',str(ROOT/'pgm_example_lyap.ipynb'),'--output','pgm_example_lyap.ipynb','--output-dir',str(ROOT),'--ExecutePreprocessor.kernel_name=pgm-owned','--ExecutePreprocessor.timeout=600']
result=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=1200)
(ROOT/f'supplementary/b5-final-{mode}.txt').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
print('command',argv,'returncode',result.returncode,flush=True)
print(result.stdout[-6000:],result.stderr[-3000:],flush=True)
assert result.returncode==0
