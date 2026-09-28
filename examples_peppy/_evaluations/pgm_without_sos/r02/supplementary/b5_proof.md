## Proof Statement

### Theorem
Let $f$ be convex and differentiable with $L$-Lipschitz gradient, $L>0$, and let $g$ be closed proper convex. Suppose $x_\star$ minimizes $h=f+g$ and $\|x_0-x_\star\|\le R$, $R\ge0$. For integer $N\ge1$, proximal gradient with step $1/L$ satisfies
$$h(x_N)-h(x_\star)\le\frac{LR^2}{4N}.$$
Write $u_k=x_k-x_\star$, $p_k=\nabla f(x_k)-\nabla f(x_\star)$, $F_k=f(x_k)-f(x_\star)$, $G_k=g(x_k)-g(x_\star)$, and $t_k=2N-k$. The following explicit Lyapunov sequence is nonincreasing:
$$V_0=0,\qquad V_N=F_N+G_N-\frac{L}{4N}\|u_0\|^2,$$
$$V_k=-\frac{L}{4N}\|u_0\|^2+\frac{L(N-k)}{t_k^2}\|u_k\|^2-\frac{\langle u_k,\nabla f(x_k)\rangle}{t_k}-\frac{\beta_k}{L}\|p_k\|^2+\frac{k+1}{t_k}F_k+\frac{k}{t_k}G_k,\quad1\le k<N.$$
Here $\beta_0=0$ and, for $1\le k<N$, the closed form is the finite matrix product
$$\beta_k=\frac{P_k}{Q_k},\qquad\binom{P_k}{Q_k}=T_kT_{k+1}\cdots T_{N-2}\binom{(N-1)/(2(N+1)^2)}{1},$$
$$T_j=\begin{pmatrix}2j(j+1)t_j(t_j-1)^2&j(j+1)(t_j-1)(j+t_j+1)\\4t_j^2(t_j-1)((2j+1)t_j-j)&2t_j^2((j^2+3j+1)t_j+1)\end{pmatrix}.$$
The empty product is the identity. No recurrence remains to be solved to evaluate this formula. For $N=1$ there are no interior coefficients or interior potentials. No value of $g(x_0)$ is required.

### Proof outline
The potential used throughout is explicitly
$$V_k=-\frac L{4N}\|u_0\|^2+\frac{L(N-k)}{(2N-k)^2}\|u_k\|^2-\frac{\langle u_k,\nabla f(x_k)\rangle}{2N-k}-\frac{\beta_k}L\|p_k\|^2+\frac{k+1}{2N-k}F_k+\frac{k}{2N-k}G_k\quad(1\le k<N),$$
with $V_0=0$, $V_N=F_N+G_N-L\|u_0\|^2/(4N)$ and the finite-product coefficients above.
For evaluated points define the nonpositive interpolation residuals
$$I_f(u,v)=f(v)-f(u)+\langle\nabla f(v),u-v\rangle+\frac{\|\nabla f(u)-\nabla f(v)\|^2}{2L},$$
$$I_g(u,v)=g(v)-g(u)+\langle g'_v,u-v\rangle.$$
Here $g'_{k+1}=L(x_k-x_{k+1})-\nabla f(x_k)\in\partial g(x_{k+1})$, and $g'_\star=-\nabla f(x_\star)$. An index in a residual denotes its iterate, and $\star$ denotes $x_\star$.
For $0\le k\le N-2$, put $t=2N-k$, $c=\beta_{k+1}$, $p=p_k$, $q=g'_{k+1}+\nabla f(x_\star)$, $r=p_{k+1}$, $z=q-Lu_k/t$, and
$$a=c+\frac{k+2}{2(t-1)},\quad d=\frac{(2k+1)t-k}{2(t-1)^2},\quad e=\frac{k+1}{2(t-1)},\quad v=\frac{k+1}{2t(t-1)},\quad w=\frac{kt+1}{2(t-1)^2},\quad\delta=d-e^2/a.$$
Define the complete nonnegative slack
$$\mathcal Q_k=\frac1L\left[a\left\|r+\frac ea z+\frac va p\right\|^2+\delta\left\|z+\frac{w-ev/a}{\delta}p\right\|^2\right].$$
For $1\le k\le N-2$ the exact step identity is
$$V_{k+1}-V_k=\frac{2N+1}{t(t-1)}I_f(\star,k+1)+\frac{k+1}{t}I_f(k,k+1)+\frac{2N}{t(t-1)}I_g(\star,k+1)+\frac{k}{t}I_g(k,k+1)-\mathcal Q_k.$$
The separate base identity, for $N\ge2$, is
$$V_1=\frac{I_f(\star,0)}{2N}+\frac{2N+1}{2N(2N-1)}I_f(\star,1)+\frac{I_f(0,1)}{2N}+\frac{I_g(\star,1)}{2N-1}-\mathcal Q_0-\frac{\|p_0\|^2}{4NL}.$$
For the terminal step let $p=p_{N-1}$, $q=g'_N+\nabla f(x_\star)$, $r=p_N$, and $u=u_{N-1}$. Then
$$\mathcal Q_{\rm end}=\frac1{2L}\left[\left\|r+q+\frac{p-Lu}{N+1}\right\|^2+\left\|q+\frac{Np-Lu}{N+1}\right\|^2\right],$$
$$V_N-V_{N-1}=\frac{I_f(\star,N)+N I_f(N-1,N)+2I_g(\star,N)+(N-1)I_g(N-1,N)}{N+1}-\mathcal Q_{\rm end}.$$
For $N=1$, use $p=p_0$, $q=g'_1+\nabla f(x_\star)$, $r=p_1$, $u=u_0$ and the same displayed $\mathcal Q_{\rm end}$ with $N=1$:
$$V_1=\tfrac12 I_f(\star,0)+\tfrac12 I_f(\star,1)+\tfrac12 I_f(0,1)+I_g(\star,1)-\mathcal Q_{\rm end}-\frac{\|p_0\|^2}{4L}.$$
All active interpolation multipliers are nonnegative. The product defining $\beta_k$ has positive entries for $1\le k<N-1$ and a positive denominator seed; hence $Q_k>0$ and $\beta_k\ge0$. For local squares $k\ge0$, $t>1$, $c\ge0$ give $a>0$ and
$$\delta=\frac{2c(t-1)((2k+1)t-k)+(k^2+3k+1)t+1}{4(t-1)^3a}>0.$$
Every square is subtracted and every residual is nonpositive, so $V_N\le\cdots\le V_1\le V_0=0$. Therefore
$$h(x_N)-h(x_\star)\le\frac{L}{4N}\|u_0\|^2\le\frac{LR^2}{4N}.$$
The exact identities, including all Gram, function-value and constant coordinates, are checked below. In one dimension $f=0$, $g(x)=LR|x|/(2N)$, $x_0=R$, and $x_\star=0$ attain equality when $R>0$; $R=0$ gives the zero bound.
