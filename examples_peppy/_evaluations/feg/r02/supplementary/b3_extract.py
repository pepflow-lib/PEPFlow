import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
workflow = (
    root
    / "supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md"
).read_text(encoding="utf-8")
blocks = re.findall(r"```python\n(.*?)```", workflow, re.S)
check = next(b for b in blocks if "certificate_checked = False" in b)
check = check.replace(
    "(REPO_ROOT / relative_path)", "(notebook_dir / relative_path)"
).replace(
    "source_path.is_relative_to(REPO_ROOT)", "source_path.is_relative_to(notebook_dir)"
)
(root / "supplementary/b3_certificate_check.py").write_text(check)
