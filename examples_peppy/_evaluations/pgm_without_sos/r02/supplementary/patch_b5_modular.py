from pathlib import Path
p=Path('supplementary/b5_symbolic_cells.py')
s=p.read_text(encoding='utf-8-sig')
marker='def check_exact(name,expression,manager):'
insert='''def local_matrix_sum(x,xnext,xstar,fun,regularizer,k,n,c,Lvalue):
    t=2*n-k
    p=fun.grad(x)-fun.grad(xstar)
    q=regularizer.grad(xnext)+fun.grad(xstar)
    r=fun.grad(xnext)-fun.grad(xstar)
    z=q-proof_weight(Lvalue/t)*(x-xstar)
    a=c+(k+2)/(2*(t-1))
    d=((2*k+1)*t-k)/(2*(t-1)**2)
    e=(k+1)/(2*(t-1))
    v=(k+1)/(2*t*(t-1))
    w=(k*t+1)/(2*(t-1)**2)
    m=(k*t*t-k*t+k+1)/(2*t*(t-1)**2)
    return (proof_weight(m/Lvalue)*p**2-proof_weight(beta_recurrence(k,n,c)/Lvalue)*p**2
        +proof_weight(d/Lvalue)*z**2+proof_weight(a/Lvalue)*r**2
        +proof_weight(2*w/Lvalue)*(p*z)+proof_weight(2*v/Lvalue)*(p*r)+proof_weight(2*e/Lvalue)*(z*r))

'''
s=s.replace(marker,insert+marker).replace('Q_step=local_square_sum(','Q_step=local_matrix_sum(').replace('-local_square_sum(x0_base','-local_matrix_sum(x0_base')
mod=Path('supplementary/b5_modular_sos.py').read_text(encoding='utf-8-sig')
mod=mod.replace("print(sp.factor(m-rec-v*v/a-(w-e*v/a)**2/delta),flush=True)","coefficient_identity=sp.factor(m-rec-v*v/a-(w-e*v/a)**2/delta)\nassert coefficient_identity==0\nprint(coefficient_identity,flush=True)")
mod=mod.replace("print('generic square identity',sp.factor(Q-squares),flush=True)","square_identity=sp.hessian(Q-squares,(p,z,r)).applyfunc(sp.factor)\nassert square_identity==sp.zeros(3)\nprint('generic Gram square identity',square_identity,flush=True)\nsquares_verified=True")
s+='\n# %% Exact quadratic square completion, valid for arbitrary vector Gram entries.\n'+mod
p.write_text(s,encoding='utf-8')
