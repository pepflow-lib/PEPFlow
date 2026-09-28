# All-horizon signs and the global square certificate

This derivation uses the current coefficient construction and algorithm.
The scalar `a_k` argument was developed collaboratively with the
current-run `certificate_hypotheses` agent and independently checked here.

## Statement and conventions

For every integer `N >= 1`, let `n=N-1`,

\[
\theta_0=1,\qquad \theta_{k+1}^2-\theta_{k+1}=\theta_k^2,
\qquad u_k=\theta_k^2,\quad u_{-1}=0,
\qquad T=u_n.
\]

Let `p_i=x_i` for `i<N`, `p_N=y_N`, and write
`p_i=x_0-sum_j H_ij g_j/L`. Put `D_i=sum_j H_ij`, `C=D_N`, and
`K=2C+1`. With `P_i=sum_(j=0)^i H_Nj`, define

\[
\beta_{-1}=0,\quad \beta_i=\frac{P_i}{2C-D_i}\ (0\le i<N),
\quad \beta_N=1,\quad \alpha_i=\beta_i-\beta_{i-1}.
\]

The denominators are positive. All `beta_i` for `0<=i<N`, all `alpha_i` for
`0<=i<=N`, and all the following edge weights are strictly positive:

\[
2w_{ij}=K\alpha_i\alpha_j-\beta_jH_{ji}
 +\beta_{j-1}H_{j-1,i}+\beta_i\mathbf1_{j=i+1},\qquad i<j.
\]

The global certificate is exactly

\[
S=L\left[\frac1{2K}\left\|r-K\sum_{i=0}^N\alpha_i v_i\right\|^2
 +\sum_{0\le i<j\le N}w_{ij}\|v_i-v_j\|^2\right],
\quad r=x_0-x_\star,\quad v_i=g_i/L.
\]

Consequently `S` is positive semidefinite for every `L>0`; its entire gradient
principal block and every nonempty principal subblock thereof are positive
definite. These statements concern exact recurrence coefficients. The saved
floating-point certificate remains finite-sample evidence separately.

## 1. Closed row and cumulative formulas

The recurrence gives `u_k-u_(k-1)=theta_k` and
`sum_(j=0)^k theta_j=u_k`. The algorithm's coefficient recurrence is

\[
h_{i+1,j}=(1-1/\theta_{i+1})h_{ij}+\theta_j/\theta_{i+1},\qquad j<i,
\quad h_{i+1,i}=1+(\theta_i-1)/\theta_{i+1}.
\]

Multiplication by `u_(i+1)` telescopes because
`1-1/theta_(i+1)=u_i/u_(i+1)`. Matching the new last coefficient and the first
row yields

\[
H_{ij}=\theta_j\left(1-\frac{u_{j-1}}{u_i}\right),\quad j<i<N.
\]

The other entries of these rows are zero. The terminal row is

\[
H_{Nj}=\theta_j\left(1-\frac{u_{j-1}}T\right),\quad 0\le j\le n.
\]

This includes `j=n`: its value is exactly `1`, since
`u_n-u_(n-1)=theta_n`. Thus `D_N=D_n+1`.

Define the genuine cumulative quantities

\[
A_k=\sum_{j=0}^k u_j,\qquad a_k=A_k/u_k,\qquad
B_k=\sum_{j=0}^k\theta_j u_{j-1}.
\]

The identity `2B_k=u_k^2-A_k` follows from initialization `B_0=0` and
`B_k-B_(k-1)=theta_k u_(k-1)`; its transition is an exact generic CAS check.
Consequently

\[
D_i+1=\frac{u_i+a_i}{2},\qquad
C=\frac{T+a_n}{2},\qquad
P_i=\frac{u_i(2T-u_i+a_i)}{2T}.
\]

For `D_i+1`, extend row `i` by its formal diagonal entry
`theta_i(1-u_(i-1)/u_i)=1`. This is only a row-sum device: the actual
nonterminal `H_ii` is zero.

## 2. A scalar invariant for the cumulative sum

For every `k>=0`,

\[
\frac{\theta_{k+1}}2\le a_k\le\frac{2\theta_{k+1}}3,
\qquad \frac13\le a_{k+1}-a_k\le\frac12.
\]

Indeed `a_0=1` and `theta_1=(1+sqrt(5))/2` satisfy the first bounds. If
`v=theta_(k+1)`, then

\[
a_{k+1}=1+(1-1/v)a_k,\qquad a_{k+1}-a_k=1-a_k/v.
\]

The assumed bounds therefore imply the increment bounds. They also imply
`(v+1)/2 <= a_(k+1) <= (2v+1)/3`. Since the theta recurrence gives
`v+1/2 < theta_(k+2) < v+1`, these imply the same bounds at index `k+1`.
The theta inequalities follow directly by comparing
`sqrt(1+4v^2)` with `2v` and `2v+1`; no asymptotic estimate is used.

In particular `a_k` and `u_k` increase. Hence `D_i<=C-1` for `i<=n`,
so `2C-D_i>=C+1>0`. All divisions above and below are justified independently
of the signs being proved.

## 3. Strict increase of q_i=beta_i/u_i

The cumulative formulas give

\[
q_i=\frac{2T-u_i+a_i}
 {T(2T+2a_n+2-u_i-a_i)}.
\]

Fix `i>=1`, and write

\[
t=\theta_i,\quad p=u_{i-1}=t^2-t,\quad a=a_{i-1},
\quad b=t-a,\quad c=(p+a)/2=(t^2-b)/2.
\]

The invariant gives `t/3<=b<=t/2`, `c>0`, and
`a_i=a+1-a/t`. Subtract the two displayed rational expressions for
`q_i,q_(i-1)`. Their denominator is positive. Their numerator is exactly
`4F_i(n)/t`, where

\[
F_i(n)=(T-p)b+c(t-a_n-1).
\]

Here `n>=i` is arbitrary. At its smallest possible value `n=i`,

\[
F_i(i)=tb+\frac{t^2-b}{2}\big((1-1/t)b-1\big).
\]

Its derivative with respect to `b` is
`(t^2+t+1)/2-(1-1/t)b`, which on `b<=t/2` is at least `t^2/2+1>0`.
Its minimum over the allowed interval is therefore

\[
F_i(i)\ge\frac{t(t-1)(3t-4)}{18}>0,
\]

because `t>=theta_1>4/3`. This is a symbolic endpoint argument with arbitrary
`i`, not a finite horizon check.

For a further horizon step, write `s=theta_(n+1)` and
`delta=a_(n+1)-a_n`. The exact transport is

\[
F_i(n+1)-F_i(n)=s b-c\delta
\ge\frac{t^2}{3}-\frac c2
\ge\frac{t^2}{12}>0.
\]

We used `s>=t`, `b>=t/3`, `delta<=1/2`, and `c<=t^2/2`.
Thus `q_i>q_(i-1)` for every allowed pair of indices. No horizon-dependent
matrix or unproved sum estimate appears in this sign argument.

## 4. Positive multipliers and edges, including all endpoints

We have `q_0=1/(2C)=1/(K-1)>0`. For `1<=i<N`,

\[
\alpha_i=u_iq_i-u_{i-1}q_{i-1}
 =\theta_iq_i+u_{i-1}(q_i-q_{i-1})>0.
\]

For `i=0`, `alpha_0=q_0`. In fact, for all `0<=i<N`,

\[
K\alpha_i>\theta_i,
\]

since `Kq_i>=Kq_0>1`. At the terminal endpoint `P_n=C` and `D_n=C-1`, so
`beta_n=C/(C+1)` and `alpha_N=1/(C+1)>0`. Thus all multipliers are positive,
and `sum_i alpha_i=1`.

For `0<=i<j<N`, substituting the closed rows gives the exact identity

\[
2w_{ij}=\alpha_j(K\alpha_i-\theta_i)
 +\theta_i u_{i-1}(q_j-q_{j-1})>0.
\]

For adjacent indices the `+beta_i` correction in the definition of `2w`
exactly replaces the absent actual entry `H_ii=0` by the formal value `1`.
Thus the displayed formula also covers `j=i+1`. At `i=0`, `u_-1=0` makes
the second term vanish and the first term is strictly positive.

For the terminal edge,

\[
2w_{iN}=\alpha_N\left[K\alpha_i-
\theta_i\left(1-\frac{u_{i-1}}T\right)\right]>0.
\]

This follows because `0<=u_(i-1)<T` and `Kalpha_i>theta_i`.
For `i=n`, the same formula uses `H_Nn=1` and the adjacent correction;
there is no missing terminal case. At `N=1`, `C=1`, `K=3`,
`alpha_0=alpha_1=beta_0=1/2`, and `w_01=1/8`, confirming the exceptional
smallest horizon exactly; no q-difference claim is needed there.

## 5. Deriving beta from the Huber null condition

The framework's actual interpolation residual is

\[
I_{ij}=f_j-f_i+\langle g_j,p_i-p_j\rangle
       +\frac1{2L}\|g_i-g_j\|^2\le0.
\]

Use star-to-all multipliers `alpha_i` and consecutive multipliers `beta_i`.
Canceling the function values in
`tau*||r||^2-(f_N-f_star)+sum lambda*I`, with `tau=L/(2K)`, gives precisely
the flow equations `alpha_i=beta_i-beta_(i-1)`, with `beta_-1=0,beta_N=1`.

To derive the remaining multiplier equations, set `L=1`, all gradients to
`1`, and `r=K`. Then `p_i=K-D_i>=C+1>1`, so the Huber function with
threshold `1` has `f_i=p_i-1/2`, gradient `1`, and `f_star=0`. Every retained
interpolation residual vanishes. Its terminal value is `K/2`, equal to
`tau*r^2`. This motivates the required PSD-certificate null vector
`[K,1,...,1]`. The following algebra verifies that null condition directly,
without presupposing PSD.

In coordinates `(r,v_0,...,v_N)`, the gradient diagonal of `S/L` is `beta_i`
for `i<N` and `1/2` for `i=N`. Its cross coefficient for `i<j` is

\[
c_{ij}=\beta_jH_{ji}-\beta_{j-1}H_{j-1,i}
        -\beta_i\mathbf1_{j=i+1}.
\]

The mixed `r,v_i` coefficient is `-alpha_i`. For `i<N`, the lower and upper
cross sums telescope respectively to

\[
\sum_{j<i}c_{ji}=\beta_iD_i-\beta_{i-1}D_{i-1}-\beta_{i-1},
\quad
\sum_{j>i}c_{ij}=H_{Ni}-\beta_i.
\]

The lower sum is empty for `i=0`; its stated expression then uses
`beta_-1=0`. Thus twice the gradient row sum is
`beta_i(D_i+1)-beta_(i-1)(D_(i-1)+1)+H_Ni`. Requiring the full row to vanish
on `[K,1,...,1]` gives exactly

\[
(2C-D_i)\alpha_i=H_{Ni}+\beta_{i-1}(D_i-D_{i-1}),
\]

or equivalently

\[
\beta_i(2C-D_i)-\beta_{i-1}(2C-D_{i-1})=H_{Ni}.
\]

Initialization `beta_-1=0` now *derives*
`beta_i(2C-D_i)=P_i`, rather than assuming the beta formula.
For `i=N`, the null equation is `C alpha_N=beta_n`, which agrees with the
already derived endpoint `beta_n=C/(C+1)`. The `r` row vanishes because
`sum alpha_i=1`. These arguments prove `S*[K,1,...,1]=0` at arbitrary `N`.

## 6. Exact square identity, including the diagonal

Expanding the proposed central square gives mixed coefficient `-alpha_i`
and gradient off-diagonal matrix entry `K alpha_i alpha_j/2`. Subtracting
the graph-Laplacian off-diagonal entry `w_ij` gives exactly `c_ij/2` by the
definition of `w_ij`.

The preceding null/row calculation is essential for the diagonal; defining
off-diagonal weights alone would not prove the identity. Let `d_i` be the
actual gradient diagonal (`beta_i`, or `1/2` at the endpoint). The verified
row identity gives `sum_(j!=i)c_ij=K alpha_i-2d_i`. Therefore the square
formula has diagonal

\[
\frac K2\alpha_i^2+\sum_{j\ne i}w_{ij}
=\frac K2\alpha_i^2+
 \frac{K\alpha_i(1-\alpha_i)-(K\alpha_i-2d_i)}2=d_i.
\]

This verifies all quadratic entries; function terms have already canceled
by flow, and both expressions have zero scalar offset. No finite matrix
inspection is used for this generic identity.

## 7. Positive gradient blocks and pivots

Set `r=0` in the square representation. A zero quadratic value forces every
`v_i=v_j`, since all edges have positive weights. The central term then forces
their common value to zero because `sum alpha_i=1`. Thus the gradient block
is strictly positive definite. Restricting a nonzero vector to any subset of
gradient coordinates proves the same fact for every nonempty principal block,
including all gradient tails.

Eliminating any ordered gradient tail therefore has strictly positive pivots:
its Schur complement quadratic is the minimum of a strictly positive definite
quadratic over the eliminated coordinates, hence remains strictly positive
definite. This justifies the denominators of reverse gradient elimination or
its equivalent scalar Riccati recurrence. After all gradients are eliminated,
the remaining `r` Schur complement is zero because of the verified Huber null
vector. In the original separate `x_0,x_star` coordinates there is also the
translation null direction. Neither of these exact null directions invalidates
the strict positivity of the gradient pivots.

## Exact verification boundary

`block5_signs_generic.py` verifies 30 exact rational identities at generic
indices, including row transport, cumulative-sum transport, the q-difference
numerator and invariant transport, generic endpoints, multiplier stationarity,
the Huber null row, adjacent/terminal edge formulas, and diagonal reconstruction.
Its only concrete horizon initialization is the legitimate `N=1` exception.
The inequalities and induction implications are established above; symbols
declared positive or sampled signs are not used as proof. The complete theorem,
native Peppy local identity, and final notebook integration belong to the root
Block 5 work and are not claimed complete by this sign lemma alone.
