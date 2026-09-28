from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
exec(
    compile(
        (ROOT / "supplementary" / "run_b1.py").read_text().split("results = []")[0],
        "bootstrap",
        "exec",
    )
)
exec(
    compile(
        (ROOT / "supplementary" / "b5_symbolic.py").read_text(), "B5-symbolic", "exec"
    )
)
exec(
    compile(
        (ROOT / "supplementary" / "b5_final_checks.py").read_text(),
        "B5-signs-normalization",
        "exec",
    )
)
