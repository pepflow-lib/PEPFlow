import runpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
namespace=runpy.run_path(str(root/'supplementary/run_b4.py'))
from numbers import Number
from typing import cast
namespace.update(Number=Number,cast=cast)
for name in ('b5_initialize.py','b5_step.py','b5_base.py','b5_boundary.py','b5_signs.py'):
    exec(compile((root/'supplementary'/name).read_text(encoding='utf-8-sig'),name,'exec'),namespace)
import json
(root/'supplementary/b5_exact_checks.json').write_text(json.dumps({'proof_checks':namespace['proof_checks'],'exact_residuals':namespace['exact_residuals'],'proof_arguments':namespace['proof_arguments']},indent=2))
