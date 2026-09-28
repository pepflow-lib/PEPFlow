from pathlib import Path

root = Path.cwd()
exec(
    compile(
        (root / "supplementary/run_b3_selected.py").read_text(encoding="utf-8-sig"),
        "run_b3_selected.py",
        "exec",
    )
)
notebook_dir = root
for filename in ("b4_sanity.py", "b4_candidates.py", "b4_search.py", "b4_basis.py"):
    source = (root / "supplementary" / filename).read_text(encoding="utf-8-sig")
    exec(compile(source, filename, "exec"))
