### Theorem
Let $f$ be convex and $L$-smooth on a finite-dimensional Euclidean space, with $L>0$, $\nabla f(x_{\star})=0$, and $\|x_{0}-x_{\star}\|^2\leq R^2$, where $R\geq0$. For every integer $N\geq1$, run the algorithm above with its special terminal recurrence. Write $g_{k}=\nabla f(x_{k})$, $f_{\star}=f(x_{\star})$, $T=\theta_{N}$, and $a=x_{0}-x_{\star}$.

A nonincreasing certificate is $V_{0}=0$, with
$$V_{k}=\frac{2\theta_{k}^{2}}{T^{2}}(f(x_{k})-f_{\star})-\frac{\theta_{k}^{2}}{LT^{2}}\|g_{k}\|^{2}+\frac{L}{2T^{2}}\left(\|z_{k+1}-x_{\star}\|^{2}-\|a\|^{2}\right),\quad 1\leq k<N,$$
and
$$V_{N}=f(x_{N})-f_{\star}+\frac{L}{2T^{2}}\left(\left\|z_{N}-x_{\star}-\frac{T}{L}g_{N}\right\|^{2}-\|a\|^{2}\right).$$
The interior range is empty when $N=1$. These expressions satisfy $V_{N}\leq\cdots\leq V_{0}=0$, and therefore
$$\boxed{f(x_{N})-f(x_{\star})\leq\frac{LR^{2}}{2\theta_{N}^{2}}.}$$
