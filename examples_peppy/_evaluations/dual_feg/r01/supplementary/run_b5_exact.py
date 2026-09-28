import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
notebook_dir=runtime.ATTEMPT
p=notebook_dir/'supplementary/run_b5_derive.py'
exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'))
for filename in ['b5_step.py','b5_base.py','b5_last.py','b5_boundary.py']:
    p=notebook_dir/'supplementary'/filename
    exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'))
(notebook_dir/'supplementary/b5-exact-checks.json').write_text(json.dumps(proof_checks,indent=2))
