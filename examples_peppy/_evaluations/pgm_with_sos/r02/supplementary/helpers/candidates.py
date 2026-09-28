"""Exact candidates inferred from this attempt's sparse duals and supplied SOS aid."""
import sympy as sp
import pepflow as pf
import pgm_setup as setup


def lambda_candidate(owner, left, right, N):
    N = sp.sympify(N)
    if left == 'x_star':
        j = int(right[2:])
        if owner == 'f':
            if j == 0:
                return 1/(2*N)
            if j == N:
                return 1/(N+1)
            return (2*N+1)/((2*N-j)*(2*N+1-j))
        if owner == 'g':
            if j == N:
                return 2/(N+1)
            return 2*N/((2*N-j)*(2*N+1-j))
    elif right != 'x_star':
        i, j = int(left[2:]), int(right[2:])
        if j == i+1:
            return (i+1)/(2*N-i) if owner == 'f' else sp.Integer(i)/(2*N-i)
    return sp.S.Zero


def sos_pieces(ctx, N):
    N=sp.sympify(N)
    L=setup.L
    astar=setup.f.grad(ctx['x_star'])
    pieces=[]
    for i in range(1,int(N)+1):
        xprev,x=ctx[f'x_{i-1}'],ctx[f'x_{i}']
        aprev,a=setup.f.grad(xprev),setup.f.grad(x)
        s=setup.g.grad(x)
        c1=N/((2*N+1-i)*(2*N-i)*L)
        u1=sp.Rational(i,2)/N*a+(2*N-i)/(2*N)*aprev-astar
        c2=(sp.Integer(i-1)/(2*N-i)*(2*N+2)/(2*N+1)+2*N/((2*N-i)**2*(2*N+1)))/(2*L)
        u2=aprev+s-L/(2*N+1-i)*(xprev-ctx['x_star'])
        c3=sp.Integer(i)/(2*N+1-i)*2*N/(2*N+1)/(2*L)
        u3=(2*N+1)/(2*N)*(a+s)-(aprev+s)/(2*N)-L/(2*N-i)*(x-ctx['x_star'])
        pieces.extend([(i,'u1',c1,u1),(i,'u2',c2,u2),(i,'u3',c3,u3)])
    return pieces


def sos_scalar(ctx,N):
    return sum((c*u**2 for _,_,c,u in sos_pieces(ctx,N)),pf.Scalar.zero())
