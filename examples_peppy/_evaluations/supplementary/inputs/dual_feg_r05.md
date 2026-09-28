# Common assumptions

All cases use real finite-dimensional Euclidean spaces, positive `L` where present, nonnegative `R`, and integer horizons `N >= 1`. Proximal updates and stated evaluations are assumed well-defined. Supply these common assumptions and only the selected case subsection to its worker.


### `dual_feg`


- Problem: monotone operators. `A` is monotone and `L`-Lipschitz.
- Initial condition: `A(x_star) = 0`, `||x_0 - x_star||^2 <= R^2`, and `z_0 = 0`.
- Parameters: fixed horizon `N >= 1` and `alpha = 1/L`.
- Performance metric: unknown.
- For `k = 0, ..., N-1`:

```text
x_{k+1/2} = x_k - alpha*z_k - alpha*A(x_k)
x_{k+1} = x_{k+1/2} - ((N-k-1)/(N-k))*alpha*(A(x_{k+1/2})-A(x_k))
z_{k+1} = ((N-k-1)/(N-k))*z_k - A(x_{k+1/2})/(N-k)
```

- Conjectured rate: unknown.

