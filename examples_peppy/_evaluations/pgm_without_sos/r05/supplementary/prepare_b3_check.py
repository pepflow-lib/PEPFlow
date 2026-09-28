import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
workflow=(root/'supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text(encoding='utf-8')
blocks=re.findall(r'```python\n(.*?)```',workflow,re.S)
source=next(s for s in blocks if 'certificate_checked = False' in s)
(root/'supplementary/b3_certificate_check.py').write_text(source,encoding='utf-8')
