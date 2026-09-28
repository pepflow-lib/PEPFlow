# Common assumptions

All cases use real finite-dimensional Euclidean spaces, positive `L` where present, nonnegative `R`, and integer horizons `N >= 1`. Proximal updates and stated evaluations are assumed well-defined. Supply these common assumptions and only the selected case subsection to its worker.


### `bppm`


- Problem: Bregman proximal point minimization. `f` is closed, proper, convex, and differentiable relative to the Bregman kernel `h`; `h` is closed, proper, convex, and differentiable.
- Define `D_h(u,v) = h(u) - h(v) - <grad h(v), u-v>`.
- Parameters: fixed `alpha > 0` and `R >= 0`.
- Initial condition: `x_star` minimizes `f`, and `D_h(x_star, x_0) <= R`. Here the radius parameter is `R`, not `R^2`.
- Metric: `f(x_N) - f(x_star)`.
- For `k = 0, ..., N-1`, `x_{k+1} = prox^h_{alpha*f}(x_k)`, meaning an exact minimizer of `alpha*f(x) + D_h(x, x_k)`.
- PEPFlow interface: `f.bregman_prox(x_k, alpha, h)`.
- Conjectured rate provided in the input: `R/(alpha*N)`.
