### Theorem

Let $f$ be convex and $L$-smooth on a Euclidean space, $L>0$, and let
$\nabla f(x_{\star})=0$, $\|x_{0}-x_{\star}\|\le R$, $R\ge0$.
For any integer $N\ge1$, initialize $y_{0}=x_{0}$, $\theta_{0}=1$ and set

$$\begin{aligned}
y_{k+1}&=x_{k}-\nabla f(x_{k})/L,\\
\theta_{k+1}&=\begin{cases}(1+\sqrt{1+4\theta_{k}^{2}})/2,&k\le N-2,\\
(1+\sqrt{1+8\theta_{k}^{2}})/2,&k=N-1,\end{cases}\\
x_{k+1}&=y_{k+1}+\frac{\theta_{k}-1}{\theta_{k+1}}(y_{k+1}-y_{k})
+\frac{\theta_{k}}{\theta_{k+1}}(y_{k+1}-x_{k}).
\end{aligned}$$

Write $g_{k}=\nabla f(x_{k})$ for $0\le k<N$, $r=x_{0}-x_{\star}$,
$h_{k}=y_{k}-x_{\star}$,
$q_{k}=\theta_{k}x_{k}-(\theta_{k}-1)y_{k}-x_{\star}$,
$s_{k}=\theta_{k}^{2}$, $Q=s_{N-1}$, $T=2Q+1$, and $\tau=L/(2T)$.
For $0\le s\le Q$, define the explicit coefficients

$$\begin{aligned}
b(s)&=\frac{s(2Q-s)}{Q(T-s)},&
A(s)&=\frac{2Q-s}{4Q(T-s)},\\
B(s)&=-\frac{s}{4Q(T-s)^{2}},&
C(s)&=\frac{s(6Q-4s+3)}{4Q(T-s)^{3}}.
\end{aligned}$$

Put $b_{k}=b(s_{k})$ for $0\le k<N$. The following closed-form potential is nonincreasing
for indices $-1,0,\ldots,N$:

$$V_{-1}=0,$$
$$\begin{aligned}
V_{k}={}&b_{k}\bigl(f(x_{k})-f(x_{\star})\bigr)
-\tau\|r\|^{2}-\frac{b_{k}}{2L}\|g_{k}\|^{2}\\
&+L\left[A(s_{k})\|q_{k+1}\|^{2}
+2B(s_{k})\langle q_{k+1},h_{k+1}\rangle
+C(s_{k})\|h_{k+1}\|^{2}\right],\quad 0\le k<N,
\end{aligned}$$
$$V_{N}=f(y_{N})-f(x_{\star})-\tau\|r\|^{2}.$$

Consequently the conjectured rate holds, and is sharp:

$$\boxed{f(y_{N})-f(x_{\star})\le
\frac{L R^{2}}{2(2\theta_{N-1}^{2}+1)}.}$$

This is an analytic alternative derived from the numerical basis structure.
It retains the auxiliary term at $k=N-1$ and has a nonzero $k=0$ expression;
it is not an exact fit to the saved numerical reverse-LDL partial sums.
The separate global interpolation certificate below is also proved exactly.
