import ast
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "supplementary/helpers/basis_structure.py").read_text(
    encoding="utf-8-sig"
)


def code(name):
    return ast.get_source_segment(
        source,
        next(
            n
            for n in ast.parse(source).body
            if isinstance(n, ast.FunctionDef) and n.name == name
        ),
    )


path = root / "state/pgm_b4.json"
state = json.loads(path.read_text())
state["coeff_code"] = code("coeff_pattern") + "\n" + code("function_coeff_pattern")
path.write_text(json.dumps(state, indent=2))
