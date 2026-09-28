### Theorem

Let $f$ be convex and $L$-smooth, $g$ closed proper convex, $L>0$, $R\ge0$, and $x_{\star}\in\arg\min(f+g)$. Assume the stated proximal updates are well-defined and $\|x_{0}-x_{\star}\|^2\le R^2$. For every integer $N\ge1$, PGM satisfies
$$h(x_{N})-h(x_{\star})\le \frac{LR^2}{4N}.$$
Here is an explicit finite-product Lyapunov certificate. Let $s_i\in\partial g(x_i)$ be the proximal subgradient for $i\ge1$, and set
$$d_i=x_i-x_{\star},\quad p_i=\frac{\nabla f(x_i)-\nabla f(x_{\star})}{L},\quad q_i=\frac{s_i+\nabla f(x_{\star})}{L},$$
$$F_i=\frac{f(x_i)-f(x_{\star})-\langle\nabla f(x_{\star}),d_i\rangle}{L},\qquad G_i=\frac{g(x_i)-g(x_{\star})+\langle\nabla f(x_{\star}),d_i\rangle}{L}.$$
Only $F_{0}$, not $G_{0}$ or $s_{0}$, is used. We have $d_{i+1}=d_i-p_i-q_{i+1}$.

For $0\le j\le N-2$, write $m_j=2N-j$ and define the explicit matrices
$$T_j=\begin{pmatrix}
2(j+1)(m_j-1)[(j+2)m_j(m_j-1)-(j+1)] &(j+1)^2(m_j-2)(2N+1)\\
4m_j^2(m_j-1)[(2j+3)m_j-(3j+4)]&2m_j^2(m_j-2)(j+1)(j+2)
\end{pmatrix}.$$
Define $z_k$ by the finite ordered product
$$\binom{P_k}{Q_k}=T_kT_{k+1}\cdots T_{N-2}\binom{N}{2(N+1)^2},\qquad z_k=\frac{P_k}{Q_k},\qquad 0\le k\le N-1.$$
The empty product is the identity, so $z_{N-1}=N/[2(N+1)^2]$. This formula has no recursively unspecified coefficients.

For $1\le k\le N-1$, let $m=2N-k$ and
$$a_k=\frac{k+1}{m},\quad b_k=\frac{k}{m},\quad A_k=\frac{N-k-1+(k+1)/(2m)-z_k}{(m-1)^2},\quad B_k=\frac1{2m}+\frac{z_k}{m-1},\quad C_k=-\frac{k-1}{2m}-z_k.$$
Then the nonincreasing sequence has the full formula
$$V_k=L\left[-\frac{\|d_0\|^2}{4N}+a_kF_k+b_kG_k-\frac{a_k}{2}\|p_k\|^2-b_k\langle p_k,q_{k+1}\rangle+A_k\|d_{k+1}\|^2+2B_k\langle d_{k+1},q_{k+1}\rangle+C_k\|q_{k+1}\|^2\right],$$
$$V_0=0,\qquad V_N=h(x_N)-h(x_{\star})-\frac{L}{4N}\|d_0\|^2.$$
There are no interior indices when $N=1$. The certificate uses one-step-ahead vectors, as in the numerically discovered Block 4 basis.
# SECTION
### Proof outline

Use the coefficient definitions and finite product in the theorem. The potential being proved is, explicitly,
$$\frac{V_k}{L}=-\frac{\|d_0\|^2}{4N}+a_kF_k+b_kG_k-\frac{a_k}{2}\|p_k\|^2-b_k\langle p_k,q_{k+1}\rangle+A_k\|d_{k+1}\|^2+2B_k\langle d_{k+1},q_{k+1}\rangle+C_k\|q_{k+1}\|^2\quad(1\le k<N),$$
with $V_0=0$ and $V_N=h(x_N)-h(x_{\star})-L\|d_0\|^2/(4N)$.

The nonpositive interpolation residuals, normalized by $L$, are
$$I_f(i,j)=\frac{f(x_j)-f(x_i)+\langle\nabla f(x_j),x_i-x_j\rangle+\|\nabla f(x_j)-\nabla f(x_i)\|^2/(2L)}{L},$$
$$I_g(i,j)=\frac{g(x_j)-g(x_i)+\langle s_j,x_i-x_j\rangle}{L}.$$
The star index means $x_{\star}$ and $s_{\star}=-\nabla f(x_{\star})$. Smooth convex interpolation gives $I_f\le0$, and convexity gives $I_g\le0$.

For $0\le k\le N-2$, put $m=2N-k$, $w=z_{k+1}$, and
$$H_k=2(m-1)^2w+(k+1)(m-2),\quad J_k=2(m-1)[(2k+3)m-(3k+4)]w+(m-2)(k+1)(k+2),$$
$$\alpha_k=\frac{H_k}{2(m-2)^2},\quad \beta_k=\frac{J_k}{2(m-1)H_k},\quad \gamma_k=\frac{2(m-1)w+(k+1)(m-2)}{H_k},\quad \delta_k=\frac{k+1}{2m\beta_k}.$$
Define the complete square contribution
$$\mathcal Q_k=\alpha_k\left\|q_{k+2}-\frac{d_{k+1}}{m-1}+\gamma_k p_{k+1}\right\|^2+\beta_k\left\|p_{k+1}+\delta_k\left(q_{k+1}-\frac{d_{k+1}}{m-1}\right)\right\|^2.$$
The matrix product gives exactly $z_k=(k+1)/(2m)-(k+1)^2/(4m^2\beta_k)$. Substitution of the PGM updates yields, for every $1\le k\le N-2$,
$$\frac{V_{k+1}-V_k}{L}=a_k I_f(k,k+1)+(a_{k+1}-a_k)I_f(\star,k+1)+b_k I_g(k,k+1)+(b_{k+1}-b_k)I_g(\star,k+1)-\mathcal Q_k.$$

For $N\ge2$, define
$$\mathcal Q_{\mathrm{init}}=\frac{\|p_0\|^2}{4N}+\frac{z_0}{(2N-1)^2}\|d_0-p_0-2Nq_1\|^2.$$
The exact base identity is
$$\frac{V_1}{L}=a_0I_f(\star,0)+a_0I_f(0,1)+(a_1-a_0)I_f(\star,1)+b_1I_g(\star,1)-\mathcal Q_0-\mathcal Q_{\mathrm{init}}.$$
The terminal identity is
$$\frac{V_N-V_{N-1}}{L}=\frac{N}{N+1}I_f(N-1,N)+\frac1{N+1}I_f(\star,N)+\frac{N-1}{N+1}I_g(N-1,N)+\frac2{N+1}I_g(\star,N)-\mathcal Q_{\mathrm{term}},$$
$$\mathcal Q_{\mathrm{term}}=\frac12\left\|p_N+\frac{N}{N+1}q_N-\frac{d_N}{N+1}\right\|^2.$$
For $N=1$, the separate identity is
$$\frac{V_1}{L}=\tfrac12 I_f(\star,0)+\tfrac12 I_f(0,1)+\tfrac12 I_f(\star,1)+I_g(\star,1)-\tfrac14\|p_0\|^2-\tfrac18\|d_0-p_0-2q_1\|^2-\tfrac12\|p_1+q_1/2-d_1/2\|^2.$$

All four entries of $T_j$ are strictly positive on $0\le j\le N-2$: here $m_j\ge j+4$, so both bracketed factors are positive. The terminal vector has positive entries, hence every $z_k>0$ and every product denominator is nonzero. Also $H_k,J_k,\alpha_k,\beta_k>0$ and all displayed denominators are positive. The weights $a_k,b_k$ are nonnegative, with
$$a_{k+1}-a_k=\frac{2N+1}{(2N-k)(2N-k-1)}>0,\qquad b_{k+1}-b_k=\frac{2N}{(2N-k)(2N-k-1)}>0.$$
Every right side is nonpositive. Thus $V_N\le V_{N-1}\le\cdots\le V_1\le V_0=0$, including the separate $N=1$ case. Rearranging the explicit terminal potential and using $L>0$ and $\|d_0\|^2\le R^2$ proves the theorem. The notebook below verifies every Gram coefficient, function-value coefficient, and offset in these identities exactly with symbolic $N,k,L$.
# SECTION
## Closed-form coefficient derivation

The Block 4 reconstruction remains the discovery input. We retain its rank-5 basis and interpolation grouping. Exact Schur elimination of the candidate slack at $N=4,6,8$ suggested that the unresolved entries depend on a single scalar $z_k$. The earlier exact samples are supporting evidence; the symbolic calculation below derives the recurrence by eliminating the two future vectors and setting the residual two-by-two matrix to zero. It then verifies that the explicit finite product solves the resulting fractional-linear recurrence with the terminal boundary condition. No numerical coefficient fit is used as an analytic proof.
# SECTION
### Closed-form conclusion

With the finite-product $z_k$ and $a_k,b_k,A_k,B_k,C_k$ defined in the theorem, the fully resolved potential is
$$V_k=L\left[-\frac{\|d_0\|^2}{4N}+a_kF_k+b_kG_k-\frac{a_k}{2}\|p_k\|^2-b_k\langle p_k,q_{k+1}\rangle+A_k\|d_{k+1}\|^2+2B_k\langle d_{k+1},q_{k+1}\rangle+C_k\|q_{k+1}\|^2\right]\quad(1\le k<N),$$
with $V_0=0$ and $V_N=h(x_N)-h(x_{\star})-L\|d_0\|^2/(4N)$. The preceding labeled coefficient matrices use the original Block 4 basis; the gradient shifts and function-gap shifts above reproduce the same full expression. The next section verifies the exact symbolic one-step identity.
# SECTION
## Symbolic Step Recursion Verification
# SECTION
For $1\le k\le N-2$, the identity being verified is
$$V_{k+1}-V_k=L\left[a_kI_f(k,k+1)+(a_{k+1}-a_k)I_f(\star,k+1)+b_kI_g(k,k+1)+(b_{k+1}-b_k)I_g(\star,k+1)-\mathcal Q_k\right].$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero in every scalar component. The symbolic context uses the actual proximal update, composite stationarity, and arbitrary $L>0$. Substituting the proved recurrence is legitimate for all product-defined $z_k$; $w=z_{k+1}$ is otherwise symbolic.
# SECTION
## Base Case and Boundary Symbolic Verification
# SECTION
For $N\ge2$, the exact base equation is
$$V_1=L\left[a_0I_f(\star,0)+a_0I_f(0,1)+(a_1-a_0)I_f(\star,1)+b_1I_g(\star,1)-\mathcal Q_0-\mathcal Q_{\mathrm{init}}\right].$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. In particular, this proves $V_1\le V_0=0$ without assuming $g(x_0)$ finite.
# SECTION
### Boundary Identity Symbolic Verification
# SECTION
For $N\ge2$, verify
$$V_N-V_{N-1}=L\left[\frac{N}{N+1}I_f(N-1,N)+\frac1{N+1}I_f(\star,N)+\frac{N-1}{N+1}I_g(N-1,N)+\frac2{N+1}I_g(\star,N)-\frac12\left\|p_N+\frac{Nq_N-d_N}{N+1}\right\|^2\right].$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. This calculation independently verifies the terminal condition $z_{N-1}=N/[2(N+1)^2]$ and the actual objective-gap normalization.
# SECTION
### Exceptional horizon $N=1$
# SECTION
Verify the separate identity
$$h(x_1)-h(x_{\star})-\frac{L}{4}\|d_0\|^2=L\left[\frac{I_f(\star,0)+I_f(0,1)+I_f(\star,1)}2+I_g(\star,1)-\frac{\|p_0\|^2}4-\frac{\|d_0-p_0-2q_1\|^2}8-\frac{\|p_1+q_1/2-d_1/2\|^2}2\right].$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. There is no interior formula or evaluation of $g(x_0)$ in this check.
# SECTION
## Signs, domains, and telescoping

All positivity obligations are explicit. For $0\le k\le N-2$, write $N=k+2+t$ with integer $t\ge0$; then $m=2N-k=k+4+2t\ge4$. The next cell expands each entry of $T_k$ in $k,t$ and checks that its coefficients and constant term are positive. Consequently the finite-product numerator and denominator are positive, since the terminal vector $(N,2(N+1)^2)$ is positive. Thus $z_k>0$ for every required index, including the empty-product boundary.

The same domain gives $(2k+3)m-(3k+4)>0$, $H_k>0$, $J_k>0$, $\alpha_k>0$, and $\beta_k>0$. Every denominator $m$, $m-1$, $m-2$, $2N-1$, $N+1$, $N$, $L$, $H_k$, and $\beta_k$ used in the proof is nonzero and positive. Neither $A_k$ nor $C_k$ is assumed positive; they occur inside the potential, not as discarded slacks. The coefficients $\gamma_k,\delta_k$ occur inside squares and need no sign assumption.

Convexity and smooth convex interpolation make the residuals nonpositive, and every multiplier is nonnegative. The displayed exact identities therefore imply $V_1\le0$, interior decrease, and terminal decrease. For $N=2$ there is no interior step, and base plus terminal suffice. The separately checked $N=1$ identity covers the remaining horizon. Therefore
$$h(x_N)-h(x_{\star})\le\frac{L}{4N}\|d_0\|^2\le\frac{LR^2}{4N}.$$
This proves the local analytic Lyapunov theorem. The numerical full-PEP certificate remains verified, while an analytic reconstruction of its entire global $\lambda,S$ is recorded separately as unresolved.
