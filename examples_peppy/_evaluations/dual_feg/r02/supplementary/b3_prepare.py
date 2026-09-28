import importlib.util
import json
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',root/'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
workflow=(root/'supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text(encoding='utf-8')
blocks=re.findall(r'```python\n(.*?)```',workflow,re.S)
check=next(b for b in blocks if b.startswith('import hashlib'))
check=check.replace('(REPO_ROOT / relative_path)', '(notebook_dir / relative_path)').replace('source_path.is_relative_to(REPO_ROOT)','source_path.is_relative_to(notebook_dir)')
check=check.replace('certificate_diff = (pb.performance_metric', 'assert pb.performance_metric is not None\ncertificate_diff = (pb.performance_metric')
(root/'supplementary/b3_certificate_check.py').write_text(check)
