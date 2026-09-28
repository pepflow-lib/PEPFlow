import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import configure  # ty: ignore[unresolved-import]

attempt, approved = configure()
workflow = (
    approved / "plugins/pepflow-workflows/skills/lyap-define/references/workflow.md"
).read_text(encoding="utf-8")
blocks = re.findall(r"```python\n(.*?)```", workflow, flags=re.S)
check = next(block for block in blocks if block.startswith("import hashlib"))
check = check.replace(
    "if not source_path.is_relative_to(REPO_ROOT):",
    'if source_path != notebook_dir / "ogm_setup.py" and str(source_path) not in json.loads((REPO_ROOT / "allowlist.json").read_text())["exact_read_files"]:',
)
(attempt / "supplementary/b3_certificate_check.py").write_text(check)
