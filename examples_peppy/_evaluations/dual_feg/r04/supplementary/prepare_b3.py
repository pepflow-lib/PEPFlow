"""Prepare exact executed sources for certificate replay and partial sums."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
workflow = (root / 'supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text(encoding='utf-8')
section = workflow.split('## Step 2', 1)[1]
check = section.split('```python\n', 1)[1].split('\n```', 1)[0]
check = check.replace('(REPO_ROOT / relative_path).resolve()', '(notebook_dir / relative_path).resolve()')
check = check.replace('source_path.is_relative_to(REPO_ROOT)', 'source_path.is_relative_to(notebook_dir)')
check = check.replace('from pepflow.constraint import ScalarConstraint, PSDConstraint', 'from pepflow.constraint import ScalarConstraint')
(root / 'supplementary/b3_certificate_check.py').write_text(check, encoding='utf-8')
