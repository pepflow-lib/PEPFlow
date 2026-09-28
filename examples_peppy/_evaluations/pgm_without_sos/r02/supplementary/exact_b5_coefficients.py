# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import contextlib

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
import sympy as sp
from pgm_setup import (  # noqa: F401 -- Required by exec of b2_notebook_cells.py.
    get_pep_setup,
)

# Preserve the recorded order of setup bindings used by exec.
# isort: split
from pgm_setup import f

notebook_dir = runtime.ROOT
with (
    (notebook_dir / "supplementary/b5-exact-LDL.log").open("w") as log,
    contextlib.redirect_stdout(log),
):
    exec(
        compile(
            (notebook_dir / "supplementary/b2_notebook_cells.py").read_text(
                encoding="utf-8-sig"
            ),
            "b2",
            "exec",
        )
    )
M = sp.Matrix(S_candidate_coords.inner_prod_coords)
pieces = {}
for index in reversed(range(M.rows)):
    pivot = sp.factor(M[index, index])
    if pivot == 0:
        assert M[:, index] == sp.zeros(M.rows, 1)
        continue
    piece = M[:, index] * M[index, :] / pivot
    pieces[index] = piece
    M = (M - piece).applyfunc(sp.factor)
assert M == sp.zeros(M.rows)
partial = sp.zeros(M.rows)
for k in range(1, N):
    for c, *_ in entries:
        if c.name == "initial_condition":
            continue
        first, second = c.name.split(":")[1].split(",")
        if second == "x_star":
            continue
        j = int(second[2:])
        if j == k or (k == 1 and j == 0):
            weight = candidate_multiplier(c.name, N)
            partial += sp.Matrix(
                pm.eval_scalar(
                    weight * (pf.Scalar.zero() + c.lhs - c.rhs), sympy_mode=True
                ).inner_prod_coords
            )
    for index, piece in pieces.items():
        label = selected["basis_vectors"][index]
        t = (
            0
            if label in ["x_0", "x_star", "grad_f(x_star)"]
            else int(label.split("x_")[1].split(")")[0])
        )
        if max(1, t) == k:
            partial -= piece
    vs = [
        ctx["x_0"] - ctx["x_star"],
        ctx[f"x_{k}"] - ctx["x_star"],
        f.grad(ctx[f"x_{k}"]) - f.grad(ctx["x_star"]),
        f.grad(ctx[f"x_{k}"]),
    ]
    B = sp.Matrix.hstack(
        *[sp.Matrix(pm.eval_vector(v, sympy_mode=True).coords) for v in vs]
    )
    P = (B.T * B).inv() * B.T
    C = (P * partial * P.T).applyfunc(sp.factor)
    print("k", k, "C", C, "b", -C[2, 2])
