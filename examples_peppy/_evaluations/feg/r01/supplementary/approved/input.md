# Common assumptions

All cases use real finite-dimensional Euclidean spaces, positive `L` where present, nonnegative `R`, and integer horizons `N >= 1`. Proximal updates and stated evaluations are assumed well-defined. Supply these common assumptions and only the selected case subsection to its worker.


### `feg`


- Problem: monotone operators. `A` is monotone and `L`-Lipschitz.
- Initial condition: `A(x_star) = 0` and `||x_0 - x_star||^2 <= R^2`.
- Metric: `||A(x_N)||^2`.
- For `k = 0, ..., N-1`:

```text
x_{k+1/2} = x_k + (x_0-x_k)/(k+1) - k*A(x_k)/((k+1)*L)
x_{k+1} = x_k + (x_0-x_k)/(k+1) - A(x_{k+1/2})/L
```

- At `k = 0`, tag `x_0` also as `x_{1/2}`; they are the same point. Do not create an independent intermediate iterate.
- Conjectured rate: unknown.
