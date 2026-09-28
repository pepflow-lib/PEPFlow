### Proof outline

For points $u,v$, use the smooth convex interpolation residual

$$\mathcal I(u,v)=f(v)-f(u)+\langle\nabla f(v),u-v\rangle
+\frac{\|\nabla f(u)-\nabla f(v)\|^{2}}{2L}\le0.$$

With the coefficients $A,B,C,b$ explicitly defined in the theorem, set

$$\begin{aligned}
\mathcal T_{s}(q,h)&=A(s)\|q\|^{2}+2B(s)\langle q,h\rangle+C(s)\|h\|^{2},\\
V_{k}&=b_{k}(f(x_{k})-f(x_{\star}))-\tau\|r\|^{2}
-\frac{b_{k}}{2L}\|g_{k}\|^{2}+L\mathcal T_{s_{k}}(q_{k+1},h_{k+1})
\quad(0\le k<N),\\
V_{-1}&=0,\qquad V_{N}=f(y_{N})-f(x_{\star})-\tau\|r\|^{2}.
\end{aligned}$$

The recurrence gives $q_{0}=r$ and
$q_{k+1}=q_{k}-2\theta_{k}g_{k}/L$, including the exceptional final update.
Define $b_{-1}=0$, $a_{k}=b_{k}-b_{k-1}$ for $0\le k<N$, and
$a_{N}=1-b_{N-1}=1/(Q+1)$.
The base identity is

$$V_{0}=b_{0}\mathcal I(x_{\star},x_{0})
-\frac{L}{32Q^{4}T}\left\|r-\frac{T}{L}g_{0}\right\|^{2}\le0.$$

Here are all the interior slack terms. For $1\le k<N$, abbreviate
$t=\theta_{k}$, $s=t^{2}$, $p=s-t=s_{k-1}$, and define

$$\begin{aligned}
P&=8Qt-6Q-4t^{3}+4t^{2}+4t-3,\\
d&=\frac{t^{2}P}{4Q(T-s)^{3}},\qquad
\gamma=\frac{3t(t-1)}{4Q(T-p)P},\qquad
\rho=\frac{T-2p}{T-p},\\
M(s)&=\begin{pmatrix}A(s)&B(s)\\B(s)&C(s)\end{pmatrix},\quad
F=\begin{pmatrix}1&0\\1/t&(t-1)/t\end{pmatrix},\quad
c=\begin{pmatrix}2t\\1\end{pmatrix},\\
\begin{pmatrix}\ell_{1}\\\ell_{2}\end{pmatrix}
&=\frac{1}{2d}\left[2F^{\mathsf T}M(s)c
-b(s)\begin{pmatrix}1/t\\(t-1)/t\end{pmatrix}
+\begin{pmatrix}0\\b(p)\end{pmatrix}\right].
\end{aligned}$$

These are explicit rational coefficients, not unknown functions. The step
identity, including both squared-norm slacks, is

$$\begin{aligned}
V_{k}-V_{k-1}={}&a_{k}\mathcal I(x_{\star},x_{k})
+b_{k-1}\mathcal I(x_{k-1},x_{k})\\
&-Ld\left\|g_{k}/L+\ell_{1}q_{k}+\ell_{2}h_{k}\right\|^{2}
-L\gamma\|q_{k}-\rho h_{k}\|^{2}.
\end{aligned}$$

Let $g_{N}=\nabla f(y_{N})$. The terminal identity is

$$\begin{aligned}
V_{N}-V_{N-1}={}&a_{N}\mathcal I(x_{\star},y_{N})
+b_{N-1}\mathcal I(x_{N-1},y_{N})\\
&-\frac{L}{2}\left\|g_{N}/L-\frac{h_{N}}{Q+1}\right\|^{2}
-\frac{L}{4(Q+1)}\left\|q_{N}-\frac{h_{N}}{Q+1}\right\|^{2}.
\end{aligned}$$

All multipliers are nonnegative. Indeed $Q\ge1$, $1\le s\le Q$,
$T-s\ge Q+1>0$, and
$b'(s)=[1-T/(T-s)^{2}]/Q>0$ on $[0,Q]$.
For the step coefficients, $t>1$ and

$$P=(8t-6)(Q-t^{2})+(4t^{3}-2t^{2}+4t-3)>0,$$

because $Q\ge t^{2}$ and
$4t^{3}-2t^{2}+4t-3=4(t-1)^{3}+10(t-1)^{2}+12(t-1)+3$.
Thus $d>0$, $\gamma\ge0$ and no denominator vanishes. The exact identities
imply $V_{N}\le\cdots\le V_{0}\le V_{-1}=0$. Hence

$$f(y_{N})-f(x_{\star})\le\tau\|r\|^{2}\le\tau R^{2}.$$

For $N=1$ the interior sum is empty; the same base and terminal identities
apply with $Q=1$. The case $R=0$ is included. The final modified
$\theta_{N}$ affects $x_{N}$ but not $y_{N}$; the auxiliary recurrence remains
valid for that update.
