# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Treat the complete verified numerical S as one PSD boundary block.
# This retains all small entries and uses no zero replacement.
S_piece_terms = {"complete_S": S_scalar}
S_assignment = {"complete_S": "boundary"}
