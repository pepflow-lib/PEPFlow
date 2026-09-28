import runpy
from pathlib import Path

scope = runpy.run_path(str(Path(__file__).with_name("run_b4.py")))
for part in ("coeff_formula", "derivation", "step", "base", "boundary", "N1"):
    exec(
        compile(
            Path(f"supplementary/b5_{part}.py").read_text(encoding="utf-8-sig"),
            part,
            "exec",
        ),
        scope,
    )
print("All four symbolic contexts passed.")
