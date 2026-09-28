"""Exact native PEPFlow step, base and terminal identity exploration."""

import json
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path[:0] = [str(root / "supplementary/approved"), str(root / "supplementary/h")]
    # local helper resolved by the notebook runtime path
    from runtime import configure  # ty: ignore[unresolved-import]

    configure()
    import sympy as sp

    # local helper resolved by the notebook runtime path
    from analytic import (  # ty: ignore[unresolved-import]
        a,
        b,
        exact_components,
        interpolation,
        local_context,
        potential_interior,
        potential_terminal,
        step_squares,
        terminal_squares,
    )

    import pepflow as pf

    ks, Ns, Ls = sp.symbols("k N L", positive=True)
    outcomes = {}
    for kind in ("step", "base", "terminal", "N1"):
        ctx, L, f, g, star, x, xn = local_context(kind)
        N = pf.Parameter("N")
        k = pf.Parameter("k")
        x0 = (
            pf.Vector(is_basis=True, tags=["x_0"])
            if kind in ("step", "terminal")
            else x
        )
        Ifstar, Igstar = interpolation(f, g, L, star, xn)
        Ifstep, Igstep = interpolation(f, g, L, x, xn)
        if kind == "step":
            lhs = potential_interior(
                xn, x0, star, f, g, L, k + 1, N
            ) - potential_interior(x, x0, star, f, g, L, k, N)
            rhs = (a(k + 1, N) - a(k, N)) * Ifstar + (b(k + 1, N) - b(k, N)) * Igstar
            rhs += (
                a(k, N) * Ifstep
                + b(k, N) * Igstep
                - sum(step_squares(x, xn, star, f, g, L, k, N), pf.Scalar.zero())
            )
        elif kind == "base":
            k = sp.S.Zero
            lhs = potential_interior(xn, x, star, f, g, L, sp.S.One, N)
            Ifinitial, _ = interpolation(f, g, L, star, x)
            rhs = a(k, N) * Ifinitial + (a(k + 1, N) - a(k, N)) * Ifstar
            rhs += (b(k + 1, N) - b(k, N)) * Igstar + a(k, N) * Ifstep
            rhs -= L / (4 * N) * ((f.grad(x) - f.grad(star)) / L) ** 2
            rhs -= sum(step_squares(x, xn, star, f, g, L, k, N), pf.Scalar.zero())
        else:
            if kind == "N1":
                N = sp.S.One
            k = N - 1
            previous = potential_interior(x, x0, star, f, g, L, k, N)
            lhs = potential_terminal(xn, x0, star, f, g, L, N) - previous
            rhs = (
                (1 - a(k, N)) * Ifstar
                + (1 - b(k, N)) * Igstar
                + a(k, N) * Ifstep
                + b(k, N) * Igstep
            )
            rhs -= sum(terminal_squares(x, xn, star, f, g, L, N), pf.Scalar.zero())
            if kind == "N1":
                Ifinitial, _ = interpolation(f, g, L, star, x)
                lhs = potential_terminal(xn, x, star, f, g, L, N)
                rhs += (
                    a(sp.S.Zero, N) * Ifinitial
                    - L / (4 * N) * ((f.grad(x) - f.grad(star)) / L) ** 2
                )
        pm = pf.ExpressionManager(ctx, resolve_parameters={"L": Ls, "N": Ns, "k": ks})
        components = exact_components(lhs - rhs, pm)
        passed = (
            all(v == 0 for comp in components[:2] for v in comp) and components[2] == 0
        )
        print(kind, passed, components if not passed else "", flush=True)
        outcomes[kind] = passed
    (root / "supplementary/b5-native-probes.json").write_text(
        json.dumps(outcomes, indent=2)
    )
    assert all(outcomes.values())


if __name__ == "__main__":
    main()
