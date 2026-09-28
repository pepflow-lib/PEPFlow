### Theorem
Under the stated assumptions, for every integer $N\ge1$,
$$h(x_{N})-h(x_{\star})\le\frac{LR^{2}}{4N}.$$
The following explicit finite-product Lyapunov certificate proves the bound. Write $d_{k}=x_{k}-x_{\star}$, $F_{k}=f(x_{k})-f(x_{\star})$, $G_{k}=g(x_{k})-g(x_{\star})$, and $m_{k}=2N-k$. For $0\le j\le N-2$, define
$$M_{j}=\begin{pmatrix}
j(j+1)m_{j}(m_{j}-1)&j(j+1)(m_{j}-1)^{2}(j+m_{j}+1)\\
(2j+1)m_{j}-j&(m_{j}-1)\bigl(j(j+3)m_{j}+m_{j}+1\bigr)
\end{pmatrix}.$$
For $0\le k<N$, set
$$\binom{u_{k}}{v_{k}}=M_{k}M_{k+1}\cdots M_{N-2}\binom{N-1}{1},\qquad T_{k}=\frac{u_{k}}{v_{k}},$$
where the product is empty for $k=N-1$. Thus $T_{N-1}=N-1$ and $T_{0}=0$, also when $N=1$. This is a nonrecursive finite-product formula; it contains no fitted or unresolved coefficients.
Set $V_{0}=0$. For $1\le k<N$, define
$$\begin{aligned}
V_{k}={}&-\frac{L}{4N}\|d_{0}\|^{2}+\frac{L(N-k)}{m_{k}^{2}}\|d_{k}\|^{2}
-\frac{\langle d_{k},\nabla f(x_{k})\rangle}{m_{k}}
-\frac{T_{k}}{2Lm_{k}^{2}}\|\nabla f(x_{k})-\nabla f(x_{\star})\|^{2}\\
&+\frac{k+1}{m_{k}}F_{k}+\frac{k}{m_{k}}G_{k}.
\end{aligned}$$
The terminal case is
$$V_{N}=h(x_{N})-h(x_{\star})-\frac{L}{4N}\|d_{0}\|^{2}.$$
Then $V_{k+1}\le V_{k}$, including the separately defined endpoints. No value of $g(x_{0})$ is required.
