# Exact Lyapunov coefficients from a finite transfer product

This derivation uses only the current study's recurrence and saved Block 4
structure. The companion code
checks exact coefficient identities and the current N=4,6,8 samples; it does not
independently establish the global positivity/kernel hypotheses used below.
The main notebook's native PEPFlow checks and the separate global sign argument
remain the owning proof checks.

## Definitions and the resulting potential

Let $q_k=g_k/L$, $s=x_0-x_\star$, and
$w_k=(y_{k+1}-x_\star,z_{k+1}-x_\star)^T$. A quadratic form in these vector
entries means the corresponding sum of inner products. Write
$K=2C_N+1$, where $C_N$ is the sum of the final output row $H_N$ in
$y_N=x_0-\sum_{i<N}H_{Ni}q_i$.

Use the current candidate multipliers

$$
\beta_{-1}=0,\qquad
\beta_i=\frac{\sum_{j=0}^{i}H_{Nj}}{2C_N-\sum_{j<i}H_{ij}}
\quad(0\le i<N),\qquad
\beta_N=1,\qquad \alpha_i=\beta_i-\beta_{i-1}.
$$

In particular, $H_{N0}=1$ gives $\beta_0=1/(K-1)$.
The unresolved state block is a symmetric $2\times2$ matrix $A_k$ normalized
by $L$. Define the formal potential for $0\le k<N$ by

$$
W_k=\beta_{k-1}(f(x_k)-f_\star)
 +L\left(w_k^T A_k w_k
 +\alpha_k\langle y_{k+1}-x_\star,q_k\rangle
 -\frac{\beta_{k-1}}2\|q_k\|^2\right).
$$

Thus in the interior basis $(y_{k+1}-x_\star,z_{k+1}-x_\star,q_k)$,

$$
C_k=L\begin{pmatrix}
(A_k)_{11}&(A_k)_{12}&\alpha_k/2\\
(A_k)_{12}&(A_k)_{22}&0\\
\alpha_k/2&0&-\beta_{k-1}/2
\end{pmatrix}.
$$

The actual initial and terminal potentials are

$$
V_0=\frac{L}{2K}\|s\|^2,\qquad
V_k=W_k\ (1\le k<N),\qquad
V_N=f(y_N)-f_\star.
$$

The exact target-normalized certificate has zero scalar offset. The saved
floating-point certificates have their original small
`bound-tau*R^2` offsets; those remain numerical evidence and were not altered.

## Backward coefficient derivation

For $0\le k\le N-2$, put $t=\theta_{k+1}$ and

$$
e=\binom10,\qquad
E_k=\begin{pmatrix}1-1/t&1/t\\0&1\end{pmatrix},\qquad
d_k=\binom1t.
$$

The update is $w_{k+1}=E_kw_k-d_kq_{k+1}$, and
$x_{k+1}-x_\star=e^TE_kw_k$.
The terminal condition is

$$
A_{N-1}=A_\mathrm{end}:=\frac{\alpha_N^2}{2}ee^T.
$$

Given $G=A_{k+1}$, define

$$
\delta_{k+1}=\beta_{k+1}-d_k^TGd_k,
\qquad v_k=\frac{\beta_ke-\beta_{k+1}E_k^Te}{2},
\qquad h_k=E_k^TGd_k+v_k.
$$

Expanding the interpolation residuals and canceling the function terms leaves
the next-gradient coefficient $\delta_{k+1}$, cross coefficient $2h_k$, and
state coefficient $A_k-E_k^TGE_k$. Completing that one square therefore forces

$$
\boxed{A_k=E_k^TA_{k+1}E_k+
             \frac{h_kh_k^T}{\delta_{k+1}}.}
$$

With $R_{ij}=f_j-f_i+\langle g_j,p_i-p_j\rangle+
\|g_i-g_j\|^2/(2L)$ and $R_{\star,k}$ in the same nonpositive convention,
the resulting exact identity is

$$
W_{k+1}-W_k
=\alpha_kR_{\star,k}+\beta_kR_{k,k+1}-Q_{k+1},
\qquad
Q_{k+1}=L\delta_{k+1}
\left\|q_{k+1}+\frac{h_k^Tw_k}{\delta_{k+1}}\right\|^2.
$$

This local algebra requires nonzero denominators. To conclude nonincrease,
the proof additionally needs the stated interpolation inequalities,
$\alpha_k,\beta_k\ge0$, and $\delta_{k+1}>0$.

## Explicit finite-product formula: no unresolved recursive coefficient

The backward recurrence can be replaced by an explicit finite matrix product.
Set $B_k=\beta_{k+1}$ and use the already defined $v_k,d_k,E_k$. Define

$$
D_k=\frac{d_kd_k^T}{B_k},\qquad
F_k=\frac{v_kv_k^T}{B_k},\qquad
\widetilde E_k=E_k+\frac{d_kv_k^T}{B_k}.
$$

Here $D_k$ denotes this transfer coefficient, not a sum of an algorithm row.
For $r_k=\beta_k/\beta_{k+1}$ and $a_k=1-1/t$,

$$
\widetilde E_k=\frac12
\begin{pmatrix}a_k+r_k&1/t\\t(r_k-a_k)&1\end{pmatrix},
\qquad \det\widetilde E_k=\frac{1-1/t}{2}>0.
$$

Define the completely specified $4\times4$ transfer matrix

$$
\mathcal T_k=
\begin{pmatrix}
\widetilde E_k^T-F_k\widetilde E_k^{-1}D_k
 &F_k\widetilde E_k^{-1}\\
-\widetilde E_k^{-1}D_k&\widetilde E_k^{-1}
\end{pmatrix}.
$$

For each $0\le k<N$, take the finite product in the displayed increasing-index
order, with an empty product equal to the $4\times4$ identity:

$$
\mathcal P_{k,N}=\mathcal T_k\mathcal T_{k+1}\cdots\mathcal T_{N-2}
=\begin{pmatrix}P_{11}&P_{12}\\P_{21}&P_{22}\end{pmatrix}.
$$

The desired coefficient block is explicitly

$$
\boxed{
A_k=(P_{11}A_\mathrm{end}+P_{12})
       (P_{21}A_\mathrm{end}+P_{22})^{-1}.
}
$$

All factors depend only on the finite theta sequence and the displayed beta
formula. The only final inverse is $2\times2$; the rank-one terminal matrix is
never inverted. This is a finite-product coefficient formula, not a fit of
floating-point coefficients.

To verify the formula, the one-factor action is

$$
G\longmapsto F_k+\widetilde E_k^T
G(I-D_kG)^{-1}\widetilde E_k.
$$

The Sherman-Morrison identity gives
$G(I-d_kd_k^TG/B_k)^{-1}
=G+Gd_kd_k^TG/(B_k-d_k^TGd_k)$, so this action is exactly the
Riccati map above. Its denominator is
$\widetilde E_k^{-1}(I-D_kG)$ and has determinant

$$
\frac{\delta_{k+1}}{\beta_{k+1}\det\widetilde E_k}.
$$

Consequently positive pivots ensure all one-factor maps, and hence the final
product denominator, are defined. Block fractional-linear maps compose by
ordinary multiplication of their $4\times4$ matrices. The companion code
verifies the map by exact cross multiplication, including the determinant
identity, without assuming an invertible $G$.

## Equivalent finite tail-Gram inverse

For an alternative explicit formula, let

$$
T_0=1,\qquad T_j=\prod_{\ell=1}^j(1-1/\theta_\ell) (j<N),
\qquad T_N=T_{N-1},
$$

$$
d_i^{\rm sep}=\frac{1-\theta_i}{T_i},\qquad
\eta_j=\beta_jT_j-\beta_{j-1}T_{j-1},
$$

where the second term in $\eta_0$ is zero. The algorithm rows satisfy
$H_{ji}=\theta_i+T_jd_i^{\rm sep}$ for $i<j$, including terminal row $j=N$.
Let $M$ be the normalized global Gram matrix in coordinates
$(s,q_0,\ldots,q_N)$. Its entries are

$$
M_{ss}=\frac1{2K},\qquad M_{s,q_i}=-\frac{\alpha_i}{2},\qquad
M_{q_i,q_i}=\begin{cases}\beta_i&i<N,\\1/2&i=N,\end{cases}
$$

$$
M_{q_i,q_j}=\frac{\alpha_j\theta_i+\eta_jd_i^{\rm sep}}2
\quad(i<j).
$$

For $J_k=\{k+1,\ldots,N\}$, form the $2\times(N-k)$ matrix with columns

$$
B_k[:,j]=\frac12
\binom{-\eta_j/T_k}{\eta_j/T_k-\alpha_j},\qquad j\in J_k.
$$

Then

$$
\boxed{A_k=B_k(M_{q_{J_k},q_{J_k}})^{-1}B_k^T.}
$$

Indeed, the past/future cross block depends on past vectors only through
$w_k$. Eliminating future gradients contributes exactly this state quadratic.
For an explicit noncircular link to the recurrence, let $B=B_{k+1}$ and let
$G_{\rm tail}$ be the gradient block on indices $k+2,\ldots,N$. The definitions
give the exact identities

$$
B_k=[\,v_k\quad E_k^TB\,],\qquad
M_{q_{J_k},q_{J_k}}=
\begin{pmatrix}
\beta_{k+1}&-d_k^TB\\
-B^Td_k&G_{\rm tail}
\end{pmatrix}.
$$

The first follows from $T_{k+1}=(1-1/\theta_{k+1})T_k$ and the definition of
$\eta_{k+1}$; the second follows from the displayed off-diagonal Gram entries.
The scalar Schur complement of the lower-right block is
$\delta_{k+1}=\beta_{k+1}-d_k^TA_{k+1}d_k$. Block inversion gives precisely the
Riccati formula. This proves the $2\times2$ coefficient identity even at k=0,
where the physical vectors $y_1-x_\star$ and $z_1-x_\star$ coincide; it does not
infer a matrix identity from a dependent physical basis.

The companion code checks these three bordered-tail component identities
symbolically. Its numerical Gram matrix was independently constructed from
the algorithm rows; all three definitions of $A_k$ agreed at N=4,6,8.

## Initial normalization from the null vector

Assume the separate global argument establishes $M\succeq0$, kernel
$\operatorname{span}\{(K,1,\ldots,1)^T\}$, and positive-definite principal
gradient tails. Those tails are automatically positive definite if this is the
full kernel: a null vector supported only on gradients has zero initial entry
and therefore cannot be a nonzero multiple of the stated kernel vector.

After eliminating gradients $q_1,\ldots,q_N$, put
$a=\boldsymbol1^TA_0\boldsymbol1$. Since $y_1=z_1=s-q_0$, the Schur matrix in
$(s,q_0)$ is

$$
\begin{pmatrix}
1/(2K)-a&-\beta_0/2+a\\
-\beta_0/2+a&\beta_0-a
\end{pmatrix}.
$$

Its kernel contains $(K,1)^T$. Using $\beta_0=1/(K-1)$, the second row gives

$$
\boxed{a=\frac{K-2}{2(K-1)^2}.}
$$

It follows exactly that

$$
V_0-W_0=Q_0,
\qquad
Q_0=\frac{LK}{2(K-1)^2}\left\|q_0-\frac{s}{K}\right\|^2.
$$

The first actual transition therefore subtracts both $Q_0$ and $Q_1$. The
target normalization is $V_0\le LR^2/(2K)$ under $\|s\|\le R$.

## Terminal identity and small horizons

The terminal square and identity are

$$
Q_N=\frac L2\|q_N-\alpha_N(y_N-x_\star)\|^2,
$$

$$
V_N-W_{N-1}
=\alpha_{N-1}R_{\star,N-1}
 +\beta_{N-1}R_{N-1,N}+\alpha_NR_{\star,N}-Q_N.
$$

Both final star terms are essential. The companion code verifies this complete
identity symbolically with independent current and terminal function gaps.

These definitions also cover N=1 using the empty transfer product:
$C_1=1$, $K=3$, $\beta_0=\alpha_0=\alpha_1=1/2$,
$A_0=A_\mathrm{end}=ee^T/8$. There are no generic interior transitions.
Combine the terminal identity with $W_0=V_0-Q_0$.
N=2 and N=3 do not require a rank-three basis at every index; the full formula
still makes sense in the possibly dependent three-vector representation.

For comparison with the saved reduced Block 4 basis at k=1, substitute

$$
z_2-x_\star=(y_2-x_\star)-(\theta_1-1)q_1.
$$

Thus $C_1^{\rm reduced}=J^TC_1J$ for
$J=\begin{pmatrix}1&0\\1&1-\theta_1\\0&1\end{pmatrix}$.
At k=N-1, the z row/column is zero because $A_{N-1}$ is supported
only on y. The initial basis is $(s)$ and the terminal quadratic basis is empty.

## Actual checks and their limits

`block5_coefficients_derivation.py` verified ten exact SymPy identities:
the full scalar polynomial step, base, and terminal identities; initial Schur
kernel identity; Riccati/transfer cross multiplication; determinant of
$\widetilde E_k$; determinant of the fractional denominator; and the three
bordered-tail component identities. The scalar
polynomial checks include independent function gaps and every quadratic
cross coefficient; the main notebook separately owns the native PEPFlow
Gram/function/offset displays.

The finite-product formula agreed with the backward Riccati computation to at
most $1.4\times10^{-17}$ over the saved sample horizons. Comparison with the
saved Block 4 numerical coefficients gave maximum absolute errors:

| N | Maximum coefficient difference | Maximum saved LDL-pivot difference |
|---|---:|---:|
| 4 | 1.992e-9 | 3.785e-9 |
| 6 | 1.033e-9 | 5.252e-10 |
| 8 | 1.516e-9 | 1.346e-9 |

Every initial, interior, penultimate, and terminal coefficient matrix was
included. The tail-Gram formula, global kernel vector, and initial sum identity
also passed the numerical checks at each sample. These sample checks do not
prove positivity for all horizons. The complete proof still requires the
separate global multiplier/sign/kernel argument and the owning notebook's
native symbolic checks; this helper does not set analytic proof flags.
