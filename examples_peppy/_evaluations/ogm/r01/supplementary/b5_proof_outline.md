### Proof outline
For evaluated points $u,v$, write $g(u)=\nabla f(u)$ and define the nonpositive smooth convex interpolation residual
$$\mathcal I(u,v)=f(v)-f(u)+\langle g(v),u-v\rangle+\frac{1}{2L}\|g(u)-g(v)\|^{2}\leq0.$$
Use $\mathcal I_{i,j}=\mathcal I(x_{i},x_{j})$ and $\mathcal I_{\star,j}=\mathcal I(x_{\star},x_{j})$.

To verify the displayed $V_{k}$, define auxiliary expressions
$$\Phi_{k}=2\theta_{k}^{2}(f(x_{k})-f_{\star})-\frac{\theta_{k}^{2}}{L}\|g_{k}\|^{2}+\frac{L}{2}\|z_{k+1}-x_{\star}\|^{2},\quad 0\leq k<N,$$
$$\Phi_{N}=T^{2}(f(x_{N})-f_{\star})+\frac{L}{2}\left\|z_{N}-x_{\star}-\frac{T}{L}g_{N}\right\|^{2},\qquad A=\frac{L}{2}\|a\|^{2}.$$
Thus $V_{k}=(\Phi_{k}-A)/T^{2}$ for $1\leq k\leq N$, while $V_{0}=0$.

The exact base, ordinary-step, and terminal-step identities are
$$\Phi_{0}-A=2\mathcal I_{\star,0},$$
$$\Phi_{j+1}-\Phi_{j}=2\theta_{j+1}\mathcal I_{\star,j+1}+2\theta_{j}^{2}\mathcal I_{j,j+1},\quad 0\leq j\leq N-2,$$
$$\Phi_{N}-\Phi_{N-1}=T\mathcal I_{\star,N}+2\theta_{N-1}^{2}\mathcal I_{N-1,N}.$$
The ordinary identity uses $\theta_{j+1}^{2}-\theta_{j+1}=\theta_{j}^{2}$; the terminal identity uses $T^{2}-T=2\theta_{N-1}^{2}$. These are the two different recurrences in the input.

In particular, for $N\geq2$,
$$V_{1}-V_{0}=\frac{2\mathcal I_{\star,0}+2\theta_{1}\mathcal I_{\star,1}+2\mathcal I_{0,1}}{T^{2}};$$
for $1\leq k\leq N-2$,
$$V_{k+1}-V_{k}=\frac{2\theta_{k+1}\mathcal I_{\star,k+1}+2\theta_{k}^{2}\mathcal I_{k,k+1}}{T^{2}};$$
and, when $N\geq2$,
$$V_{N}-V_{N-1}=\frac{T\mathcal I_{\star,N}+2\theta_{N-1}^{2}\mathcal I_{N-1,N}}{T^{2}}.$$
For $N=1$, $T=2$ and the direct identity is
$$V_{1}=\frac{2\mathcal I_{\star,0}+2\mathcal I_{\star,1}+2\mathcal I_{0,1}}{4}.$$
Every multiplier is nonnegative: $\theta_{0}=1$, the ordinary recurrence preserves $\theta_{j}\geq1$, and the terminal recurrence gives $T\geq2$. All divisions are valid since $L>0$ and $T>0$. Thus all displayed increments are nonpositive.

Finally, the terminal formula gives
$$f(x_{N})-f_{\star}=V_{N}+\frac{L}{2T^{2}}\|a\|^{2}-\frac{L}{2T^{2}}\left\|z_{N}-x_{\star}-\frac{T}{L}g_{N}\right\|^{2}\leq\frac{LR^{2}}{2T^{2}}.$$
This uses the nonnegative terminal square and the initial radius bound, and includes $R=0$. The notebook below verifies each identity in all symbolic scalar components. The proof is local and valid for arbitrary horizon; a separate global analytic multiplier-table verification is not claimed.
