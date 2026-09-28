# Domain: integer N>=1, integer 1<=i<=N, and L>0.
i_sign, n_sign = sp.symbols('i N',integer=True,positive=True)
alpha_difference = sp.factor(alpha(i_sign+1,n_sign)-alpha(i_sign,n_sign))
beta_difference = sp.factor(beta(i_sign,n_sign)-beta(i_sign-1,n_sign))
assert sp.cancel(alpha_difference-(2*n_sign+1)/((2*n_sign-i_sign)*(2*n_sign+1-i_sign))) == 0
assert sp.cancel(beta_difference-2*n_sign/((2*n_sign-i_sign)*(2*n_sign+1-i_sign))) == 0
assert sp.cancel(1-alpha(n_sign,n_sign)-1/(n_sign+1)) == 0
assert sp.cancel(1-beta(n_sign-1,n_sign)-2/(n_sign+1)) == 0
print('Exact multiplier differences and terminal simplifications checked.')
print('For 1<=i<=N: 2N-i>=N>=1 and 2N+1-i>=N+1; all multipliers and all three SOS weights are nonnegative.')
print('Each local RHS is therefore <=0. V_0=0 and V_N=gap-L*||x_0-x_star||^2/(4N), giving gap<=L*R^2/(4N).')
# Sharpness for R>0: f=0, g(x)=c*max(x,0), c=L*R/(2N), x_0=R, x_star=0.
r_sharp = sp.Symbol('R',nonnegative=True)
c_sharp = ell_sym*r_sharp/(2*n_sym)
xn_sharp = r_sharp-n_sym*c_sharp/ell_sym
assert sp.simplify(xn_sharp-r_sharp/2) == 0
assert sp.simplify(c_sharp*xn_sharp-ell_sym*r_sharp**2/(4*n_sym)) == 0
print('Exact sharpness value for the one-dimensional hinge example:',sp.factor(c_sharp*xn_sharp))
