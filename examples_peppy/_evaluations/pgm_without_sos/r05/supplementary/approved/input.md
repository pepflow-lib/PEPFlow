# Common assumptions

All cases use real finite-dimensional Euclidean spaces, positive `L` where present, nonnegative `R`, and integer horizons `N >= 1`. Proximal updates and stated evaluations are assumed well-defined. Supply these common assumptions and only the selected case subsection to its worker.


### `pgm`


- Problem: composite convex minimization. `f` is convex and `L`-smooth; `g` is closed, proper, and convex. Write `h = f + g`.
- Initial condition: `x_star` minimizes `h`, and `||x_0 - x_star||^2 <= R^2`.
- Metric: `h(x_N) - h(x_star)`.
- For `k = 0, ..., N-1`, set `x_{k+1} = prox_{g/L}(x_k - grad f(x_k)/L)`.
- Conjectured rate: unknown.

### `pgm_without_sos`


- No fixed SOS aid is supplied. Derive the certificate and Lyapunov analysis within this attempt. You may discover and use an SOS decomposition yourself.
- Do not read the supplied fixed aid, its source, either condition's pre-existing answers, sibling outputs, or any other attempt's artifacts, including the paired repetition.

