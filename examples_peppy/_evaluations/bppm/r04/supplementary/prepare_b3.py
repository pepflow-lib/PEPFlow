from pathlib import Path

root = Path(__file__).resolve().parents[1]
w = (
    root
    / "supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md"
).read_text()
part = w.split("## Step 2")[1].split("## Step 3")[0]
check = (
    part.split("```python\n")[1].split("```")[0].replace("REPO_ROOT", "notebook_dir")
)
(root / "supplementary/b3_check.py").write_text(check)
part = w.split("## Step 6")[1].split("## Step 7")[0]
coverage = part.split("```python\n")[1].split("```")[0]
(root / "supplementary/b3_coverage.py").write_text(coverage)
