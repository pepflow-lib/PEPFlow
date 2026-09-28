from pathlib import Path

p = Path("supplementary/certificate_check.py")
s = (
    p.read_text()
    .replace("(REPO_ROOT / relative_path)", "(NOTEBOOK_DIR / relative_path)")
    .replace(
        "source_path.is_relative_to(REPO_ROOT)",
        "source_path.is_relative_to(NOTEBOOK_DIR)",
    )
)
p.write_text(s)
