import sys
import json
import subprocess
from pathlib import Path
root=Path(__file__).resolve().parent.parent
settings=json.loads((root/'supplementary/approved/settings.json').read_text())
args=settings['preflight_command'][:-1]
args[args.index('--evidence')+1]=str(root/'supplementary'/sys.argv[1])
args[args.index('--helper-root')+1]=str(root/'supplementary/helpers')
args[args.index('--probe-helper-path')+1]='supplementary/helpers/runtime.py'
args+=['check','--','pgm_setup.py','pgm_example_lyap.ipynb','supplementary/helpers/runtime.py','supplementary/helpers/candidates.py']
raise SystemExit(subprocess.run(args,cwd=root).returncode)
