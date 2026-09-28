import re
from pathlib import Path
root=Path.cwd()
text=(root/'supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text(encoding='utf-8')
blocks=re.findall(r'```python\n(.*?)```',text,re.S)
check=next(b for b in blocks if b.startswith('import hashlib'))
(root/'supplementary/b3_certificate_check.py').write_text(check)
coverage=next(b for b in blocks if b.startswith('boundary_names'))
(root/'supplementary/b3_coverage.py').write_text(coverage)
