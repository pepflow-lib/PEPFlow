### Proof outline
The potential is $V_{0}=0$,
$$V_{k}=-\frac{L}{4N}\|d_{0}\|^{2}+\frac{L(N-k)}{m_{k}^{2}}\|d_{k}\|^{2}-\frac{\langle d_{k},\nabla f(x_{k})\rangle}{m_{k}}-\frac{LT_{k}}{2m_{k}^{2}}\|p_{k}\|^{2}+a_{k}F_{k}+b_{k}G_{k}\quad(1\le k<N),$$
and $V_{N}=F_{N}+G_{N}-L\|d_{0}\|^{2}/(4N)$, where $a_{k}=(k+1)/m_{k}$, $b_{k}=k/m_{k}$, and $p_{k}=(\nabla f(x_{k})-\nabla f(x_{\star}))/L$. The $T_{k}$ are the explicit finite products in the theorem.
Let $s_{i}\in\partial g(x_{i})$ be the proximal subgradient for $i\ge1$, and take $s_{\star}=-\nabla f(x_{\star})$. Define the nonpositive interpolation residuals
$$I^{f}_{i,j}=f(x_{j})-f(x_{i})+\langle\nabla f(x_{j}),x_{i}-x_{j}\rangle+\frac{\|\nabla f(x_{i})-\nabla f(x_{j})\|^{2}}{2L}\le0,$$
$$I^{g}_{i,j}=g(x_{j})-g(x_{i})+\langle s_{j},x_{i}-x_{j}\rangle\le0.$$
For $0\le k\le N-2$, put $m=m_{k}$, $U=T_{k+1}$ and
$$\begin{aligned}
H&=U+(k+2)(m-1),\\
D&=((2k+1)m-k)U+(m-1)(k(k+3)m+m+1),\\
r&=\frac{(k+1)(m-1)}{H},\qquad
c=\frac{mH(km+1)-(k+1)^{2}(m-1)^{2}}{mD},\\
A&=\frac{H}{2(m-1)^{2}},\qquad B=\frac{D}{2(m-1)^{2}H}.
\end{aligned}$$
Let $q_{k+1}=(s_{k+1}+\nabla f(x_{\star}))/L$ and $w_{k}=q_{k+1}-d_{k}/m$. The update gives $d_{k+1}=d_{k}-p_{k}-q_{k+1}$. Define the nonnegative local remainder
$$Q_{k}=L A\left\|p_{k+1}+r\left(w_{k}+\frac{p_{k}}{m}\right)\right\|^{2}+L B\|w_{k}+cp_{k}\|^{2}.$$
Splitting the first transfer matrix from the product gives exactly
$$T_{k}=\frac{k(k+1)(m-1)\bigl(mU+(m-1)(k+m+1)\bigr)}{D}.$$
Expanding all inner products and function values yields, for $1\le k\le N-2$,
$$V_{k+1}-V_{k}=(a_{k+1}-a_{k})I^{f}_{\star,k+1}+a_{k}I^{f}_{k,k+1}+(b_{k+1}-b_{k})I^{g}_{\star,k+1}+b_{k}I^{g}_{k,k+1}-Q_{k}.$$
For $N\ge2$, the initial identity is
$$V_{1}=a_{0}I^{f}_{\star,0}-\frac{L}{4N}\|p_{0}\|^{2}+(a_{1}-a_{0})I^{f}_{\star,1}+a_{0}I^{f}_{0,1}+b_{1}I^{g}_{\star,1}-Q_{0}.$$
For the terminal step, with $p=p_{N-1}$, $z=p_{N}$, $q=q_{N}$, and $d=d_{N-1}$, set
$$Q_{\mathrm{end}}=\frac L2\left\|z+q-\frac{d-p}{N+1}\right\|^{2}+\frac L2\left\|q+\frac{N}{N+1}p-\frac{d}{N+1}\right\|^{2}.$$
Using $T_{N-1}=N-1$ gives
$$V_{N}-V_{N-1}=\frac1{N+1}I^{f}_{\star,N}+\frac N{N+1}I^{f}_{N-1,N}+\frac2{N+1}I^{g}_{\star,N}+\frac{N-1}{N+1}I^{g}_{N-1,N}-Q_{\mathrm{end}}.$$
For $N=1$, the independently verified identity is
$$V_{1}=\tfrac12 I^{f}_{\star,0}-\tfrac L4\|p_{0}\|^{2}+\tfrac12 I^{f}_{\star,1}+\tfrac12 I^{f}_{0,1}+I^{g}_{\star,1}-Q_{\mathrm{end}},$$
where the terminal square formula is evaluated at $N=1$.
For every product factor, $j\ge0$ and $m_{j}>1$. Its entries are nonnegative and its second row is strictly positive. Starting with $(N-1,1)$ proves $v_{k}>0$ and $T_{k}\ge0$. Hence $H,D,A,B>0$. Also
$$a_{k+1}-a_{k}=\frac{2N+1}{m_{k}(m_{k}-1)}>0,\qquad b_{k+1}-b_{k}=\frac{2N}{m_{k}(m_{k}-1)}>0.$$
All residual weights are nonnegative, so the exact identities imply the required nonincreasing direction. Consequently,
$$h(x_{N})-h(x_{\star})\le\frac{L}{4N}\|d_{0}\|^{2}\le\frac{LR^{2}}{4N}.$$
The constant is attained in one dimension by $f=0$, $g(x)=LR|x|/(2N)$, $x_{0}=R$, and $x_{\star}=0$: the iterates satisfy $x_{k}=R(1-k/(2N))$ and the terminal gap equals $LR^{2}/(4N)$.
