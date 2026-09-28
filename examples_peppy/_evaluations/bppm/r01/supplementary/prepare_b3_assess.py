import re
from pathlib import Path
root=Path.cwd()
workflow=(root/'supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text(encoding='utf-8')
blocks=re.findall(r'```python\n(.*?)```',workflow,re.S)
assess=next(b for b in blocks if b.startswith('def assess_rank_pattern'))
(root/'supplementary/b3_assess.py').write_text(assess)
