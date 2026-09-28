### Theorem
Let $h=f+g$, with $f$ convex and differentiable with $L$-Lipschitz gradient, $L>0$, and $g$ closed, proper and convex. Suppose $x_{\star}$ minimizes $h$ and $\|x_{0}-x_{\star}\|^{2}\le R^{2}$, $R\ge0$. For any integer $N\ge1$, proximal gradient with step $1/L$ satisfies
$$h(x_{N})-h(x_{\star})\le\frac{L\|x_{0}-x_{\star}\|^{2}}{4N}\le\frac{LR^{2}}{4N}.$$
Here is a nonincreasing Lyapunov certificate. Write $a_{k}=\nabla f(x_{k})$, $a_{\star}=\nabla f(x_{\star})$, $d_{k}=x_{k}-x_{\star}$ and $D_{k}=2N-k$. Define $V_{0}=0$ and
$$V_{k}=\frac{k+1}{D_{k}}[f(x_{k})-f(x_{\star})]+\frac{k}{D_{k}}[g(x_{k})-g(x_{\star})]-\frac{\langle a_{k},d_{k}\rangle}{D_{k}}+\frac{\|a_{k}-a_{\star}\|^{2}}{2LD_{k}}+\frac{L(N-k)}{D_{k}^{2}}\|d_{k}\|^{2}-\frac{L}{4N}\|d_{0}\|^{2},\qquad 1\le k<N.$$
The terminal case is defined separately:
$$V_{N}=h(x_{N})-h(x_{\star})-\frac{L}{4N}\|d_{0}\|^{2}.$$
Then $V_{N}\le V_{N-1}\le\cdots\le V_{0}=0$. The statement also covers $N=1$ and $R=0$; it requires no finite value of $g(x_{0})$.
