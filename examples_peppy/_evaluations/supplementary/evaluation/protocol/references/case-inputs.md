# Case inputs

Packet assembly reference: extract only **Common assumptions** and the worker's own case subsection. For `case_id=pgm`, also extract only its selected **PGM condition notice**; append **Fixed PGM SOS Aid** only for `condition_id=pgm_with_sos`. Never include the aid or the other condition notice in a `pgm_without_sos` packet. Do not dispatch this entire collection or expose another case's input. The formulas and mathematical assumptions below are frozen; preserve their normalization and assistance distinctions across repetitions. Both PGM conditions use the identical `pgm` problem subsection, including its unknown rate. This file contains no evaluator targets or controller provenance.

## Common assumptions

All cases use real finite-dimensional Euclidean spaces, positive `L` where present, nonnegative `R`, and integer horizons `N >= 1`. Proximal updates and stated evaluations are assumed well-defined. Supply these common assumptions and only the selected case subsection to its worker.

### `pgm`

- Problem: composite convex minimization. `f` is convex and `L`-smooth; `g` is closed, proper, and convex. Write `h = f + g`.
- Initial condition: `x_star` minimizes `h`, and `||x_0 - x_star||^2 <= R^2`.
- Metric: `h(x_N) - h(x_star)`.
- For `k = 0, ..., N-1`, set `x_{k+1} = prox_{g/L}(x_k - grad f(x_k)/L)`.
- Conjectured rate: unknown.

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

### `bppm`

- Problem: Bregman proximal point minimization. `f` is closed, proper, convex, and differentiable relative to the Bregman kernel `h`; `h` is closed, proper, convex, and differentiable.
- Define `D_h(u,v) = h(u) - h(v) - <grad h(v), u-v>`.
- Parameters: fixed `alpha > 0` and `R >= 0`.
- Initial condition: `x_star` minimizes `f`, and `D_h(x_star, x_0) <= R`. Here the radius parameter is `R`, not `R^2`.
- Metric: `f(x_N) - f(x_star)`.
- For `k = 0, ..., N-1`, `x_{k+1} = prox^h_{alpha*f}(x_k)`, meaning an exact minimizer of `alpha*f(x) + D_h(x, x_k)`.
- PEPFlow interface: `f.bregman_prox(x_k, alpha, h)`.
- Conjectured rate provided in the input: `R/(alpha*N)`.

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

## PGM condition notices

### `pgm_with_sos`

- Authorized assistance: the fixed SOS aid below, supplied from the start. Record it as supplied assistance. Derive the remaining certificate and Lyapunov analysis within this attempt.
- The aid is a candidate, not a verified certificate or proof. Verify it against this attempt's certificate and all applicable block gates.

### `pgm_without_sos`

- No fixed SOS aid is supplied. Derive the certificate and Lyapunov analysis within this attempt. You may discover and use an SOS decomposition yourself.
- Do not read the supplied fixed aid, its source, either condition's pre-existing answers, sibling outputs, or any other attempt's artifacts, including the paired repetition.

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
