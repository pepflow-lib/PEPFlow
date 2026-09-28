### Theorem
Under the assumptions above, for every integer $N\geq1$,
$$h(x_{N})-h(x_{\star})\leq\frac{LR^{2}}{4N}.$$
Here is an explicit Lyapunov certificate. Put $e_{k}=x_{k}-x_{\star}$, $p_{k}=(\nabla f(x_{k})-\nabla f(x_{\star}))/L$, and $t_{k}=2N-k$. Set $V_{0}=0$, and for $1\leq k<N$ set
$$V_{k}=-\frac{\|e_{0}\|^{2}}{4N}+\frac{k+1}{Lt_{k}}(f(x_{k})-f(x_{\star}))+\frac{k}{Lt_{k}}(g(x_{k})-g(x_{\star}))+\frac{N-k}{t_{k}^{2}}\|e_{k}\|^{2}-\frac{\langle e_{k},\nabla f(x_{k})\rangle}{Lt_{k}}-\beta_{k}\|p_{k}\|^{2}.$$
The terminal value is
$$V_{N}=\frac{h(x_{N})-h(x_{\star})}{L}-\frac{\|e_{0}\|^{2}}{4N}.$$
The coefficient has the following closed finite-product expression. For $1\leq j\leq N-2$, with $t=2N-j$, define
$$M_{j}=\begin{pmatrix}2j(j+1)t(t-1)^{2}&j(j+1)(t-1)(j+t+1)\\4t^{2}(t-1)((2j+1)t-j)&2t^{2}((j^{2}+3j+1)t+1)\end{pmatrix}.$$
For $1\leq k<N$, form
$$\binom{u_{k}}{v_{k}}=\left(M_{k}M_{k+1}\cdots M_{N-2}\right)\binom{(N-1)/(2(N+1)^{2})}{1},\qquad\beta_{k}=u_{k}/v_{k}.$$
An empty product is the identity; thus $\beta_{N-1}=(N-1)/(2(N+1)^{2})$. Set $\beta_{0}=\beta_{N}=0$. No product or interior potential is needed when $N=1$. Every denominator is positive on the stated domain. These formulas give $V_{k+1}\leq V_{k}$, including the exceptional first and last steps.
