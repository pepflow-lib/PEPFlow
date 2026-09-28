# Common assumptions

All cases use real finite-dimensional Euclidean spaces, positive `L` where present, nonnegative `R`, and integer horizons `N >= 1`. Proximal updates and stated evaluations are assumed well-defined. Supply these common assumptions and only the selected case subsection to its worker.


### `ogm`


- Problem: smooth convex minimization. `f` is convex and `L`-smooth.
- Initial condition: `grad f(x_star) = 0`, `||x_0 - x_star||^2 <= R^2`, and `z_0 = x_0`.
- Metric: `f(x_N) - f(x_star)`.
- Define `theta_{-1} = 0`; for `0 <= k < N`, `theta_k = (1 + sqrt(1 + 4*theta_{k-1}^2))/2`; set `theta_N = (1 + sqrt(1 + 8*theta_{N-1}^2))/2`.
- For `k = 0, ..., N-1`:

```text
y_{k+1} = x_k - grad f(x_k)/L
z_{k+1} = z_k - (2*theta_k/L)*grad f(x_k)
x_{k+1} = (1 - 1/theta_{k+1})*y_{k+1} + z_{k+1}/theta_{k+1}
```

- Conjectured rate: unknown. Preserve the special terminal `theta_N` recurrence.
