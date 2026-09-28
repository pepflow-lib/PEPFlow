# Executed by the OGM notebook in a shared namespace with the required globals.
# Not a standalone script; validate it through notebook execution.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Exact algebraic recurrence for the proposed auxiliary vector."""

# Work componentwise: a vector identity follows from this scalar linear identity.
t, T, x, y, g, smoothness = sp.symbols("t T x y g L", nonzero=True)
y_next = x - g / smoothness
x_next = y_next + (t - 1) / T * (y_next - y) + t / T * (y_next - x)
auxiliary_identity_residual = sp.expand(
    T * x_next - (T - 1) * y_next - (t * x - (t - 1) * y - 2 * t * g / smoothness)
)
assert auxiliary_identity_residual == 0
print("Exact auxiliary recurrence residual:", auxiliary_identity_residual)

# Verify the two equivalent constructions in the actual selected context too.
theta = b4_theta_values(N_int)
q_running = initial_gap()
auxiliary_coordinate_errors = []
for k in range(N_int + 1):
    error = float(
        np.max(
            np.abs(pm.eval_vector(auxiliary_gap(k) - q_running).coords.astype(float))
        )
    )
    assert error < 1e-12
    auxiliary_coordinate_errors.append(error)
    if k < N_int:
        q_running -= 2 * theta[k] / params_sp["L"] * current_gradient(k)
print("Largest auxiliary coordinate residual:", max(auxiliary_coordinate_errors))
