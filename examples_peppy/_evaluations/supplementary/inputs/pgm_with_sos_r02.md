# Common assumptions

All cases use real finite-dimensional Euclidean spaces, positive `L` where present, nonnegative `R`, and integer horizons `N >= 1`. Proximal updates and stated evaluations are assumed well-defined. Supply these common assumptions and only the selected case subsection to its worker.


### `pgm`


- Problem: composite convex minimization. `f` is convex and `L`-smooth; `g` is closed, proper, and convex. Write `h = f + g`.
- Initial condition: `x_star` minimizes `h`, and `||x_0 - x_star||^2 <= R^2`.
- Metric: `h(x_N) - h(x_star)`.
- For `k = 0, ..., N-1`, set `x_{k+1} = prox_{g/L}(x_k - grad f(x_k)/L)`.
- Conjectured rate: unknown.

### `pgm_with_sos`


- Authorized assistance: the fixed SOS aid below, supplied from the start. Record it as supplied assistance. Derive the remaining certificate and Lyapunov analysis within this attempt.
- The aid is a candidate, not a verified certificate or proof. Verify it against this attempt's certificate and all applicable block gates.

## Fixed PGM SOS Aid


Only a `pgm_with_sos` worker receives this section. This is a candidate decomposition of the nonnegative full-PEP slack. It does not provide the convergence bound, dual multipliers, partial sums, or final Lyapunov function.

For `i = 1, ..., N`, write `a_i = grad f(x_i)`, `a_star = grad f(x_star)`, and choose the proximal subgradient `s_i in partial g(x_i)` given by `s_i = L*(x_{i-1}-x_i) - a_{i-1}`. Define:

```text
c1_i = N / ((2*N+1-i)*(2*N-i)*L)
u1_i = (i/(2*N))*a_i + ((2*N-i)/(2*N))*a_{i-1} - a_star

c2_i = (((i-1)/(2*N-i))*((2*N+2)/(2*N+1))
        + (2*N)/((2*N-i)^2*(2*N+1))) / (2*L)
u2_i = a_{i-1} + s_i - (L/(2*N+1-i))*(x_{i-1}-x_star)

c3_i = (i/(2*N+1-i))*((2*N)/(2*N+1))/(2*L)
u3_i = ((2*N+1)/(2*N))*(a_i+s_i) - (a_{i-1}+s_i)/(2*N)
        - (L/(2*N-i))*(x_i-x_star)

S_candidate = sum(c1_i*||u1_i||^2 + c2_i*||u2_i||^2 + c3_i*||u3_i||^2
                  for i = 1, ..., N)
```

These are mathematical formulas, not directly executable Python. Define `a_0 = grad f(x_0)`. Use exact arithmetic when implementing them. Verify their role against the certificate obtained in this attempt, accounting explicitly for any overall certificate normalization.
