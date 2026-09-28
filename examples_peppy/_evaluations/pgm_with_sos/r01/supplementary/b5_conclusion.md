## Closed-form coefficient conclusion
The numerical pattern suggests the following normalized solution; the generic coefficient equations below derive its current-step coefficients from the preceding potential and the candidate local residual weights. Base and terminal equations then verify its normalization without assuming endpoint extrapolation.

In the ordered basis $[a_{\star},d_{0},d_{k},a_{k}-a_{\star}]$, the only nonzero entries of the symmetric coefficient matrix are
$$C_{11}=-\frac{L}{4N},\quad C_{22}=\frac{L(N-k)}{(2N-k)^{2}},\quad C_{33}=\frac{1}{2L(2N-k)},\quad C_{02}=C_{20}=C_{23}=C_{32}=-\frac{1}{2(2N-k)}.$$
Indices here are zero based. The function coefficients are $(k+1)/(2N-k)$ and $k/(2N-k)$, with zero constant offset. Hence
$$V_{k}=\frac{k+1}{2N-k}(f_{k}-f_{\star})+\frac{k}{2N-k}(g_{k}-g_{\star})-\frac{\langle a_{k},d_{k}\rangle}{2N-k}+\frac{\|a_{k}-a_{\star}\|^{2}}{2L(2N-k)}+\frac{L(N-k)}{(2N-k)^{2}}\|d_{k}\|^{2}-\frac{L}{4N}\|d_{0}\|^{2},\quad1\le k<N.$$
Take $V_{0}=0$ and $V_{N}=h_{N}-h_{\star}-L\|d_{0}\|^{2}/(4N)$. The following sections derive and verify the one-step identity and both boundaries. Numerical matrix comparisons are diagnostics only; arbitrary-horizon validity follows from exact symbolic residuals.
