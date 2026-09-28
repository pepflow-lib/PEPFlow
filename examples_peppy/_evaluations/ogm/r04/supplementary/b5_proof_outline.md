### Proof outline
Use the smooth convex interpolation residual
$$I_{i,j}=f(x_{j})-f(x_{i})+\langle g_{j},x_{i}-x_{j}\rangle+\frac{1}{2L}\|g_{i}-g_{j}\|^{2}\leq0,$$
with $g_{\star}=0$. This inequality follows directly from smooth convexity: apply the descent inequality to $h(u)=f(u)-\langle g_{j},u\rangle$, whose minimum is attained at $x_{j}$, to get $h(x_{i})-h(x_{j})\geq\|g_{i}-g_{j}\|^{2}/(2L)$.

Write $W_{k}=H^{2}V_{k}$. Thus $W_{0}=0$,
$$W_{k}=2\theta_{k}^{2}F_{k}+\frac L2(\|q_{k}\|^{2}-\|d_{0}\|^{2})-\frac{\theta_{k}^{2}}L\|g_{k}\|^{2}\quad(1\leq k<N),$$
and $W_{N}=H^{2}F_{N}+\frac L2(\|q_{N}\|^{2}-\|d_{0}\|^{2})$.

For $N\geq2$, the initialization $z_{0}=x_{0}$ and $\theta_{0}=1$ give
$$W_{1}=2I_{\star,0}+2\theta_{1}I_{\star,1}+2I_{0,1}.$$
For $1\leq k\leq N-2$, substitution of the algorithm and $\theta_{k+1}^{2}-\theta_{k+1}=\theta_{k}^{2}$ gives
$$W_{k+1}-W_{k}=2\theta_{k+1}I_{\star,k+1}+2\theta_{k}^{2}I_{k,k+1}.$$
The special terminal relation $H^{2}-H=2\theta_{N-1}^{2}$ gives
$$W_{N}-W_{N-1}=H I_{\star,N}+2\theta_{N-1}^{2}I_{N-1,N}.$$
For $N=1$, $H=2$ and the direct initialization identity is
$$W_{1}=2I_{\star,0}+2I_{\star,1}+2I_{0,1}.$$
All five identities, including the boundary normalization below, are checked exactly in the final symbolic cells in every Gram, function-value, and constant coordinate. The local symbols represent arbitrary adjacent theta values; polynomial reduction uses precisely the stated recurrence, not a finite horizon sample.

The defining theta formulas imply $\theta_{k}\geq1$ by induction and $H\geq2$. All interpolation multipliers and $\tau=L/(2H^{2})$ are therefore positive, and all denominators used in the proof are nonzero. The identities show $V_{N}\leq\cdots\leq V_{0}=0$. Finally,
$$F_{N}-\frac{LR^{2}}{2H^{2}}=V_{N}-\tau\|q_{N}\|^{2}+\tau(\|d_{0}\|^{2}-R^{2})\leq0.$$
This establishes the stated bound also at $R=0$, without division by $R$.

For completeness, telescoping the displayed identities gives the global full-PEP identity for every horizon:
$$F_{N}-\frac{LR^{2}}{2H^{2}}-\tau(\|d_{0}\|^{2}-R^{2})-\sum_{j=0}^{N-1}\frac{2\theta_{j}}{H^{2}}I_{\star,j}-\frac1H I_{\star,N}-\sum_{j=0}^{N-1}\frac{2\theta_{j}^{2}}{H^{2}}I_{j,j+1}+\tau\|q_{N}\|^{2}=0.$$
Thus the candidate global multipliers and rank-one remainder are justified analytically as well as numerically. No other interpolation families or extra constraints occur in this setup.
