import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from runtime import configure
attempt,approved = configure()
import re
workflow = (approved/'plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text()
blocks = re.findall(r'```python\n(.*?)```',workflow,flags=re.S)
assess = next(b for b in blocks if b.startswith('def assess_rank_pattern'))
(attempt/'supplementary/b3_rank_assess.py').write_text(assess)
