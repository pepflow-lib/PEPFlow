import re
from pathlib import Path
root=Path.cwd()
w=(root/'supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text(encoding='utf-8-sig')
section=w[w.index('## Step 2'):w.index('## Step 3')]
code=re.search(r'```python\n(.*?)```',section,re.S).group(1)
(root/'supplementary/certificate_check.py').write_text(code)
