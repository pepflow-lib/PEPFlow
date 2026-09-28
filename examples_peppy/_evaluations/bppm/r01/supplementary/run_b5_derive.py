import sys
from pathlib import Path
root=Path.cwd()
exec(compile((root/'supplementary/save_b4.py').read_text(encoding='utf-8-sig'),'save_b4.py','exec'))
for filename in ('b5_derivation.py','b5_step.py'):
    source=(root/'supplementary'/filename).read_text(encoding='utf-8-sig')
    exec(compile(source,filename,'exec'))
