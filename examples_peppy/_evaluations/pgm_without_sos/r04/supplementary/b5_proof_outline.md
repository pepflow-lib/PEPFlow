### Proof outline
Use the potential $V_{0}=0$,
$$V_{k}=-\frac{\|e_{0}\|^{2}}{4N}+a_{k}\frac{f(x_{k})-f(x_{\star})}{L}+b_{k}\frac{g(x_{k})-g(x_{\star})}{L}+A_{k}\|e_{k}\|^{2}-d_{k}\langle e_{k},\nabla f(x_{k})/L\rangle-\beta_{k}\|p_{k}\|^{2}$$
for $1\leq k<N$, with $a_{k}=(k+1)/t_{k}$, $b_{k}=k/t_{k}$, $A_{k}=(N-k)/t_{k}^{2}$, $d_{k}=1/t_{k}$ and the finite-product $\beta_{k}$ defined in the theorem. Its terminal value is $V_{N}=(h(x_{N})-h(x_{\star}))/L-\|e_{0}\|^{2}/(4N)$.

For a selected subgradient $s_{g}(v)\in\partial g(v)$, define the nonpositive interpolation residuals
$$J_{f}(u,v)=\frac{f(v)-f(u)+\langle\nabla f(v),u-v\rangle}{L}+\frac{\|\nabla f(u)-\nabla f(v)\|^{2}}{2L^{2}},\qquad J_{g}(u,v)=\frac{g(v)-g(u)+\langle s_{g}(v),u-v\rangle}{L}.$$
Take $s_{g}(x_{\star})=-\nabla f(x_{\star})$ and $s_{g}(x_{k+1})=L(x_{k}-x_{k+1})-\nabla f(x_{k})$. Put $q_{k+1}=(s_{g}(x_{k+1})+\nabla f(x_{\star}))/L$; then $e_{k+1}=e_{k}-p_{k}-q_{k+1}$.

For $0\leq k\leq N-2$, set $t=2N-k$, $c=\beta_{k+1}$, and
$$H_{k}=\begin{pmatrix}c+\frac{k+2}{2(t-1)}&\frac{k+1}{2(t-1)}\\\frac{k+1}{2(t-1)}&\frac{(2k+1)t-k}{2(t-1)^{2}}\end{pmatrix},\quad K_{k}=\begin{pmatrix}-\frac{k+1}{2t(t-1)}&\frac{k+1}{2t(t-1)}\\-\frac{(2k+1)t-k}{2t(t-1)^{2}}&\frac{kt+1}{2(t-1)^{2}}\end{pmatrix}.$$
Writing $z=(e_{k},p_{k})^{T}$ and $w=(p_{k+1},q_{k+1})^{T}$, let
$$Q_{k}=\|w+H_{k}^{-1}K_{k}z\|_{H_{k}}^{2},\qquad\|y\|_{H}^{2}=\sum_{i,j=1}^{2}H_{ij}\langle y_{i},y_{j}\rangle.$$
The exact interior identity, for $1\leq k\leq N-2$, is
$$V_{k+1}-V_{k}=(a_{k+1}-a_{k})J_{f}(x_{\star},x_{k+1})+a_{k}J_{f}(x_{k},x_{k+1})+(b_{k+1}-b_{k})J_{g}(x_{\star},x_{k+1})+b_{k}J_{g}(x_{k},x_{k+1})-Q_{k}.$$
For $N\geq2$, the base identity is
$$V_{1}=a_{0}J_{f}(x_{\star},x_{0})+(a_{1}-a_{0})J_{f}(x_{\star},x_{1})+a_{0}J_{f}(x_{0},x_{1})+b_{1}J_{g}(x_{\star},x_{1})-Q_{0}-\frac{\|p_{0}\|^{2}}{4N}.$$
No value or subgradient of $g$ at $x_{0}$ is required.

For the final step define $z=(e_{N-1},p_{N-1})^{T}$, $w=(p_{N},q_{N})^{T}$, and
$$H_{T}=\begin{pmatrix}1/2&1/2\\1/2&1\end{pmatrix},\quad K_{T}=\begin{pmatrix}-\frac1{2(N+1)}&\frac1{2(N+1)}\\-\frac1{N+1}&1/2\end{pmatrix},\quad Q_{T}=\|w+H_{T}^{-1}K_{T}z\|_{H_{T}}^{2}.$$
For $N\geq2$,
$$V_{N}-V_{N-1}=\frac1{N+1}J_{f}(x_{\star},x_{N})+\frac{N}{N+1}J_{f}(x_{N-1},x_{N})+\frac2{N+1}J_{g}(x_{\star},x_{N})+\frac{N-1}{N+1}J_{g}(x_{N-1},x_{N})-Q_{T}.$$
For $N=1$, the separate identity is
$$V_{1}=\tfrac12J_{f}(x_{\star},x_{0})+\tfrac12J_{f}(x_{\star},x_{1})+\tfrac12J_{f}(x_{0},x_{1})+J_{g}(x_{\star},x_{1})-Q_{T}-\tfrac14\|p_{0}\|^{2}.$$
Every multiplier is nonnegative. The positive-entry transfer matrices imply $\beta_{k}\geq0$ and $v_{k}>0$. For $t>1$, $k\geq0$, $c\geq0$, the first diagonal entry of $H_{k}$ is positive, and
$$\det H_{k}=\frac{2c(t-1)((2k+1)t-k)+(k^{2}+3k+1)t+1}{4(t-1)^{3}}>0.$$
Thus $Q_{k}\geq0$; also $H_{T}\succ0$ because its leading principal minors are $1/2$ and $1/4$. The identities imply $V_{N}\leq V_{0}=0$. Consequently
$$h(x_{N})-h(x_{\star})=L\left(V_{N}+\frac{\|e_{0}\|^{2}}{4N}\right)\leq\frac{L\|e_{0}\|^{2}}{4N}\leq\frac{LR^{2}}{4N}.$$
The symbolic cells below verify every Gram, function-value and constant coordinate, including the exceptional $N=1$ case. The local analytic proof does not assert a separate global closed-form full-PEP certificate.
