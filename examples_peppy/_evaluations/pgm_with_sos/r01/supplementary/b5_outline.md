### Proof outline
Use $a_{k}=\nabla f(x_{k})$, $s_{i}=L(x_{i-1}-x_{i})-a_{i-1}\in\partial g(x_{i})$, $s_{\star}=-a_{\star}$, and $d_{k}=x_{k}-x_{\star}$. The interpolation residuals are
$$I_{f}(u,v)=f(v)-f(u)+\langle\nabla f(v),u-v\rangle+\frac{\|\nabla f(u)-\nabla f(v)\|^{2}}{2L}\le0,$$
$$I_{g}(u,v)=g(v)-g(u)+\langle s_{v},u-v\rangle\le0.$$
Define $D_{k}=2N-k$, $V_{0}=0$, $V_{N}=h(x_{N})-h(x_{\star})-L\|d_{0}\|^{2}/(4N)$, and, for $1\le k<N$,
$$V_{k}=\frac{(k+1)[f(x_{k})-f(x_{\star})]+k[g(x_{k})-g(x_{\star})]-\langle a_{k},d_{k}\rangle}{D_{k}}+\frac{\|a_{k}-a_{\star}\|^{2}}{2LD_{k}}+\frac{L(N-k)\|d_{k}\|^{2}}{D_{k}^{2}}-\frac{L\|d_{0}\|^{2}}{4N}.$$
For $1\le i\le N$, set $Q_{i}=\sum_{r=1}^{3}c_{i,r}\|u_{i,r}\|^{2}$, where
$$c_{i,1}=\frac{N}{(2N+1-i)(2N-i)L},\qquad u_{i,1}=\frac{i}{2N}a_{i}+\frac{2N-i}{2N}a_{i-1}-a_{\star},$$
$$c_{i,2}=\frac{1}{2L}\left[\frac{i-1}{2N-i}\frac{2N+2}{2N+1}+\frac{2N}{(2N-i)^{2}(2N+1)}\right],\qquad u_{i,2}=a_{i-1}+s_{i}-\frac{L}{2N+1-i}d_{i-1},$$
$$c_{i,3}=\frac{i}{2N+1-i}\frac{2N}{2N+1}\frac{1}{2L},\qquad u_{i,3}=\frac{2N+1}{2N}(a_{i}+s_{i})-\frac{a_{i-1}+s_{i}}{2N}-\frac{L}{2N-i}d_{i}.$$
Let
$$\alpha_{i}=\begin{cases}\dfrac{2N+1}{(2N-i)(2N+1-i)}&i<N,\\ \dfrac{1}{N+1}&i=N,\end{cases}\quad
\beta_{i}=\begin{cases}\dfrac{2N}{(2N-i)(2N+1-i)}&i<N,\\ \dfrac{2}{N+1}&i=N.\end{cases}$$
The exact identity for every step is
$$V_{i}-V_{i-1}=\mathbf{1}_{\{i=1\}}\frac{I_{f}(x_{\star},x_{0})}{2N}+\alpha_{i}I_{f}(x_{\star},x_{i})+\frac{i}{2N+1-i}I_{f}(x_{i-1},x_{i})+\beta_{i}I_{g}(x_{\star},x_{i})+\frac{i-1}{2N+1-i}I_{g}(x_{i-1},x_{i})-Q_{i}.$$
The last $I_{g}$ term is **omitted** for $i=1$, avoiding an evaluation of $g(x_{0})$. For $N=1$, use the terminal multipliers and the initial residual together. The notebook verifies the interior, base, terminal, and $N=1$ identities separately, in all scalar components with symbolic parameters.

All multipliers and square coefficients are nonnegative: $2N-i\ge N>0$, $2N+1-i\ge N+1>0$, $L>0$, and $i-1\ge0$. Thus each displayed right-hand side is nonpositive. Telescoping yields $V_{N}\le V_{0}=0$, so $h(x_{N})-h(x_{\star})\le L\|d_{0}\|^{2}/(4N)\le LR^{2}/(4N)$. The use of a supplied SOS candidate is justified by these exact identities, not by numerical agreement.
