## Exact global interpolation certificate

This section closes the all-horizon PSD question left open in Block 2.
The candidate weights are unchanged, while the numerical certificate is
preserved as a separate artifact. Let $m=N-1$, $s_{-1}=0$, $b_{N}=1$,
$p_{i}=x_{i}$ for $i<N$, $p_{N}=y_{N}$, $g_{i}=\nabla f(p_{i})$, and
$a_{i}=b_{i}-b_{i-1}$. The exact scalar identity is

$$S=\tau\|r\|^{2}+\sum_{i=0}^{N}a_{i}\mathcal I(x_{\star},p_{i})
+\sum_{i=0}^{m}b_{i}\mathcal I(p_{i},p_{i+1})
-\bigl(f(y_{N})-f(x_{\star})\bigr).$$

Function values cancel by $a_{i}=b_{i}-b_{i-1}$. Define

$$\begin{aligned}
c_{i}&=\frac{g_{i}-g_{i+1}}{T-s_{i}},&
J&=\frac12\sum_{i=0}^{m}s_{i}^{2}c_{i},&
\mu_{j}&=\frac{s_{j-1}+s_{j}}2,\\
U_{j}&=\sum_{i=j}^{m}(s_{i}-\mu_{j})c_{i}-J/Q,&
W_{j}&=\sum_{i=j}^{m}c_{i}.&&
\end{aligned}$$

Then a finite algebraic sum of squares proves $S\ge0$:

$$\boxed{S=\frac{L}{2T}\left\|r-\frac{T}{L}\sum_{i=0}^{N}a_{i}g_{i}\right\|^{2}
+\frac{\|J\|^{2}}{LQ^{2}}
+\sum_{j=0}^{m}\left[\frac{3\theta_{j}}{LQ}\|U_{j}\|^{2}
+\frac{\theta_{j}^{3}}{4LQ}\|W_{j}\|^{2}\right].}$$

### Generic derivation of the global squares

Put $d_{j}=s_{j}^{2}-s_{j-1}^{2}=(2\theta_{j}-1)s_{j}$ and
$z_{j}=g_{j}/L$. Since $s_{j}-s_{j-1}=\theta_{j}$,
$\sum_{j=0}^{i}\theta_{j}=s_{i}$ and $\sum_{j=0}^{i}d_{j}=s_{i}^{2}$.
The actual point coordinates are

$$p_{i}-x_{\star}=r-\sum_{j<i}\left(2\theta_{j}-\frac{d_{j}}{s_{i}}\right)z_{j}
\quad(i<N),$$
$$p_{N}-x_{\star}=r-\sum_{j=0}^{m}\left(2\theta_{j}-\frac{d_{j}}Q\right)z_{j}.$$

For completeness, the point-coordinate induction has two coefficient cases.
With $v=\theta_{k+1}$, $\theta_{k}^{2}=v^{2}-v$, an old gradient has
$w=\theta_{j}$ and $d=d_{j}$ and obeys

$$\left(1-\frac1v\right)\left(2w-\frac{d}{v^{2}-v}\right)+\frac{2w}{v}
=2w-\frac{d}{v^{2}}.$$

For the new gradient, the difference between the proposed and actual
coefficients, multiplied by $v^{2}$, is
$(2\theta_{k}-1)(v^{2}-v-\theta_{k}^{2})=0$.
The initial point has an empty sum. At the output the last coefficient is
$2\theta_{m}-d_{m}/Q=1$, exactly the final gradient step.
The modified $\theta_{N}$ is not used in this induction.

Expanding the interpolation quadratic gives

$$\frac SL=\frac{\|r\|^{2}}{2T}-\left\langle r,\sum_{i}a_{i}z_{i}\right\rangle
+\sum_{i,j}K_{ij}\langle z_{i},z_{j}\rangle,$$

where $u_{i}=b_{i}/s_{i}$ for $i<N$, $u_{N}=1/Q$,
$e_{i}=u_{i}-u_{i-1}$, and

$$K_{ii}=b_{i}\ (i<N),\quad K_{NN}=\tfrac12,\quad
K_{ij}=\theta_{j}a_{i}-\tfrac12d_{j}e_{i}\ (i>j).$$

For $H=K-(T/2)aa^{\mathsf T}$, the exact row identity is $H\mathbf1=0$.
Define $u(s)=(2Q-s)/[Q(T-s)]$, extending $u_{i}=b_{i}/s_{i}$.
An ordinary row, with $s=t^{2}$ and $p=s-t$, is checked by

$$b(s)+p\bigl(b(s)-b(p)\bigr)-\frac{p^{2}}2\bigl(u(s)-u(p)\bigr)
+t(1-b(s))-\frac{s^{2}-p^{2}}2(1/Q-u(s))
=\frac T2\bigl(b(s)-b(p)\bigr).$$

At $i=0$ the formal $u(0)$ term is multiplied by $p^{2}=0$.
The terminal row reduces to $(1+Qa_{N})/2=Ta_{N}/2$.
If $(Dz)_{i}=z_{i}-z_{i+1}$, then $H=D^{\mathsf T}\mathcal M D$,
where $\mathcal M_{ij}=\sum_{a\le i,b\le j}H_{ab}$.
The prefix diagonal of $K$ telescopes to $s_{j}b_{j}$ using
$1+2p-p^{2}/s=s$. Summing the remaining off-diagonal prefixes gives

$$\begin{aligned}
\mathcal M_{ij}
&=b_{i}(s_{j}-Tb_{j}/2)-s_{j}^{2}u_{i}/2+s_{j}b_{j}/2\\
&=\frac{s_{j}^{2}(3Qs_{i}-Qs_{j}-s_{i}^{2})}
{2Q^{2}(T-s_{i})(T-s_{j})},\qquad i\ge j.
\end{aligned}$$

The symmetric numerator kernel has an elementary integral representation:

$$\begin{aligned}
\mathcal W(x,y)
&=\min(x,y)^{2}\bigl(3Q\max(x,y)-Q\min(x,y)-\max(x,y)^{2}\bigr)\\
&=6Q\int_{0}^{Q}(x-t)_{+}(y-t)_{+}\,dt-x^{2}y^{2}.
\end{aligned}$$

For $F(t)=\sum_{i}c_{i}(s_{i}-t)_{+}$, one has $J=\int_{0}^{Q}F(t)\,dt$.
Completing the $r$ square yields

$$S=\frac{L}{2T}\left\|r-\frac{T}{L}\sum_{i}a_{i}g_{i}\right\|^{2}
+\frac{3}{LQ}\int_{0}^{Q}\|F(t)-J/Q\|^{2}\,dt+\frac{\|J\|^{2}}{LQ^{2}}.$$

On $[s_{j-1},s_{j}]$ this centered affine function has midpoint value
$U_{j}$, slope $-W_{j}$, and width $\theta_{j}$, so its integral is
$\theta_{j}\|U_{j}\|^{2}+\theta_{j}^{3}\|W_{j}\|^{2}/12$.
This proves the displayed finite SOS for every horizon. The following
exact rational and integral checks verify the generic identities used
above; the additional finite-horizon checks are corroboration only.
