"""Test an index-pattern relaxation and inspect its fractions and factors."""
import json
import sys
from fractions import Fraction
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path[:0] = [str(root / "supplementary/approved"), str(root / "supplementary/h"), str(root)]
    from runtime import configure
    configure()
    import numpy as np
    from certificate import capture, inventory
    from pgm_setup import get_pep_setup
    params = {"L": 1, "R": 1}
    ctx, pb, obj = get_pep_setup(4, params)
    dropped = []
    for c, origin, _, _ in inventory(ctx, pb):
        if origin == "initial":
            continue
        first, second = c.name.split(":")[1].split(",")
        keep = first == "x_star"
        if first != "x_star" and second != "x_star":
            keep = int(second[2:]) == int(first[2:]) + 1
        if not keep:
            dropped.append(c.name)
    pb.set_relaxed_constraints(dropped)
    dense = json.loads((root / "state/pgm_dense.json").read_text())
    state = capture(ctx, pb, obj, params, dense["opt_value"])
    (root / "supplementary/b2-pattern.json").write_text(json.dumps(state, indent=2))
    print("Pattern", state["opt_value"], state["numerical_checks"])
    for name, value in state["named_dual_values"].items():
        if value is not None:
            print(name, value, str(Fraction(value).limit_denominator(1000)))
    D = np.asarray(state["numerical_decomposition"]["D"])
    E = np.asarray(state["numerical_decomposition"]["ell_coords"])
    print("basis", state["basis_vectors"])
    print("D diagonal", np.diag(D))
    print("ell", np.round(E, 5))


if __name__ == "__main__":
    main()
