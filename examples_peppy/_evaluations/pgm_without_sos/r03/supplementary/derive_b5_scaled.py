exec(compile(open('supplementary/derive_b5_recurrence.py',encoding='utf-8-sig').read(),'derive','exec'))
m,T,U=sp.symbols('m T U',positive=True)
sub={n:(m+k)/2,t:T/(2*m**2),u:U/(2*(m-1)**2)}
Mt=M.subs(sub).applyfunc(sp.factor)
print('scaled M',Mt)
rec=sp.factor(sp.solve(sp.factor(r[1,1].subs(sub)),T)[0])
print('Trec',rec)
print('Trec difference k',sp.factor(rec-k))
# terminal initialize T_(n-1)=n-1; compute symbolic backwards and seek simplified recurrence using surplus T-k
v=sp.symbols('v')
print('surplus rec',sp.factor((rec-k).subs(U,v+k+1)))

