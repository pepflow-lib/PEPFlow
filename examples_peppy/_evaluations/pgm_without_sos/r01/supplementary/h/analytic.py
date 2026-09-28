"""A simple closed coefficient choice in the discovered basis."""
import sympy as sp
import pepflow as pf


def a(k, N):
    return (k+1)/(2*N-k)


def b(k, N):
    return k/(2*N-k)


def distance_weight(k, N):
    return (N-k)/(2*N-k)**2


def gradient_weight(k, N):
    return k/(2*(2*N-k)**2)


def potential_interior(x, x0, star, f, g, L, k, N):
    d = x-star
    p = f.grad(x)-f.grad(star)
    return (-L/(4*N)*(x0-star)**2
            +L*distance_weight(k,N)*d**2
            -1/(2*N-k)*d*f.grad(x)
            -gradient_weight(k,N)/L*p**2
            +a(k,N)*(f(x)-f(star))+b(k,N)*(g(x)-g(star)))


def potential_terminal(x, x0, star, f, g, L, N):
    return f(x)+g(x)-f(star)-g(star)-L/(4*N)*(x0-star)**2


def sos_coefficients(k, N):
    m = 2*N-k
    aa = gradient_weight(k+1,N)+(k+2)/(2*(m-1))
    bb = (k+1)/(2*(m-1))
    cc = (k*m+N-k)/(m-1)**2
    dd = (k+1)/(2*m*(m-1))
    ee = (k*m+1)/(2*(m-1)**2)
    ff = a(k,N)/2-distance_weight(k+1,N)-gradient_weight(k,N)
    beta = cc-bb**2/aa
    eta = ee-bb*dd/aa
    gamma = ff-dd**2/aa-eta**2/beta
    return aa, beta, gamma, bb/aa, dd/aa, eta/beta


def step_squares(x, xn, star, f, g, L, k, N):
    p = (f.grad(x)-f.grad(star))/L
    q = (f.grad(xn)-f.grad(star))/L
    s = (g.grad(xn)+f.grad(star))/L
    z = s-(x-star)/(2*N-k)
    alpha,beta,gamma,u,v,w = sos_coefficients(k,N)
    return [L*alpha*(q+u*z+v*p)**2,
            L*beta*(z+w*p)**2, L*gamma*p**2]


def terminal_squares(x, xn, star, f, g, L, N):
    p = (f.grad(x)-f.grad(star))/L
    q = (f.grad(xn)-f.grad(star))/L
    s = (g.grad(xn)+f.grad(star))/L
    d = x-star
    return [L/2*(q+s+(p-d)/(N+1))**2,
            L/2*(s+(N*p-d)/(N+1))**2]


def interpolation(f, g, L, u, v):
    If = f(v)-f(u)+f.grad(v)*(u-v)+(f.grad(u)-f.grad(v))**2/(2*L)
    Ig = g(v)-g(u)+g.grad(v)*(u-v)
    return If, Ig


def finite_pieces(ctx, f, g, L, N):
    """PSD per-step pieces for exact rational indices."""
    N = sp.S(N)
    star = ctx["x_star"]
    pieces, assignment = {}, {}
    p0 = (f.grad(ctx["x_0"])-f.grad(star))/L
    pieces["initial_smooth_square"] = L/(4*N)*p0**2
    assignment["initial_smooth_square"] = 0
    for index in range(int(N)):
        k = sp.S(index)
        x,xn = ctx[f"x_{index}"],ctx[f"x_{index+1}"]
        local = terminal_squares(x,xn,star,f,g,L,N) if k == N-1 else step_squares(x,xn,star,f,g,L,k,N)
        for j,piece in enumerate(local):
            name=f"step_{index}_square_{j}"
            pieces[name]=piece
            assignment[name]=index
    return pieces, assignment


def exact_components(expression, manager):
    evaluated=manager.eval_scalar(expression,sympy_mode=True)
    gram=sp.Matrix(evaluated.inner_prod_coords).applyfunc(sp.factor)
    functions=sp.Matrix(list(evaluated.func_coords)).applyfunc(sp.factor)
    offset=sp.factor(evaluated.offset)
    return gram,functions,offset


def local_context(tag):
    ctx=pf.PEPContext(tag).set_as_current()
    L=pf.Parameter("L")
    f=pf.SmoothConvexFunction(is_basis=True,tags=[f"f_{{{tag}}}"],L=L)
    g=pf.ConvexFunction(is_basis=True,tags=[f"g_{{{tag}}}"])
    star=(f+g).set_stationary_point("x_star")
    x=pf.Vector(is_basis=True,tags=["x"])
    xn=g.prox(x-f.grad(x)/L,1/L,tag="x_next")
    f(xn)
    g(x)
    return ctx,L,f,g,star,x,xn
