import sys
from pathlib import Path
root=Path.cwd()
exec(compile((root/'supplementary/run_b5_derive.py').read_text(encoding='utf-8-sig'),'run_b5_derive.py','exec'))
for filename in ('b5_base.py','b5_boundary.py','b5_signs.py'):
    source=(root/'supplementary'/filename).read_text(encoding='utf-8-sig')
    exec(compile(source,filename,'exec'))
