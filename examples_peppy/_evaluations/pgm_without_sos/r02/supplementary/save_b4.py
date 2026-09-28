# Serialize the actual reconstructed numerical structure; no solve or search here.
b4_source=(notebook_dir/'supplementary/b4_notebook_cells.py').read_text(encoding='utf-8-sig')
basis_code=b4_source[b4_source.index('def V_k_basis(k):'):b4_source.index('for k in range(N+1):\n    selected_basis')]
structure_definition=b4_source[b4_source.index('def V_k_structure(k):'):b4_source.index('component_residuals={}')] 
structure_code='function_coefficients = '+repr(function_coefficients)+'\n'+structure_definition
unknowns=[]
quadratic={}
for i in range(4):
    for j in range(i,4):
        name=f'c_{i}{j}'
        quadratic[f'{i},{j}']=name+'(k,N,L)'
        unknowns.append(dict(name=name,arguments=['k','N','L'],role=f'interior.C[{i},{j}] = interior.C[{j},{i}]',index_domain='1 <= k <= N-1'))
for name,role,domain,args in [('alpha','coefficient of f(x_k)-f_star','1 <= k <= N-1',['k','N','L']),('beta','coefficient of g(x_k)-g_star','1 <= k <= N-1',['k','N','L']),('c_terminal','terminal quadratic coefficient','k=N',['N','L']),('alpha_terminal','terminal f-gap coefficient','k=N',['N','L']),('beta_terminal','terminal g-gap coefficient','k=N',['N','L'])]:
    unknowns.append(dict(name=name,arguments=args,role=role,index_domain=domain))
expression_structure=dict(quadratic_convention='V_quadratic = sum_{i,j} C_ij * <v_i,v_j>; symmetric C; off-diagonal entries counted twice',
 interior={'index_domain':'1 <= k <= N-1; left=1,right=1','basis_labels':['x_0-x_star','x_k-x_star','grad_f(x_k)-grad_f(x_star)','grad_f(x_k)'],'quadratic_coefficients':quadratic},
 initial={'index_domain':'k=0','basis_labels':[],'quadratic_coefficients':{},'value':'0'},
 terminal={'index_domain':'k=N','basis_labels':['x_0-x_star'],'quadratic_coefficients':{'0,0':'c_terminal(N,L)'}},
 function_terms=[{'index_domain':'1 <= k <= N-1','expression':'f(x_k)-f(x_star)','coefficient':'alpha(k,N,L)'},
                 {'index_domain':'1 <= k <= N-1','expression':'g(x_k)-g(x_star)','coefficient':'beta(k,N,L)'},
                 {'index_domain':'k=N','expression':'f(x_N)-f(x_star)','coefficient':'alpha_terminal(N,L)'},
                 {'index_domain':'k=N','expression':'g(x_N)-g(x_star)','coefficient':'beta_terminal(N,L)'}],constant_terms=[])
state={**b3,'basis_templates':{'interior':expression_structure['interior']['basis_labels'],'initial':[],'terminal':['x_0-x_star']},
 'basis_code':basis_code,'structure_code':structure_code,'coeff_by_k':{str(k):C.tolist() for k,C in coeff_by_k.items()},
 'coeff_code':None,'coefficient_formula_status':'unresolved','expression_structure':expression_structure,'unresolved_coefficients':unknowns,
 'numerical_reconstruction':{'certificate_id':b3['certificate_id'],'required_indices':list(range(N+1)),
    'quadratic_residuals':{str(k):v for k,v in coefficient_residuals.items()},'component_residuals':component_residuals,
    'tolerances':{'indep_tol':1e-7,'span_tol':1e-5,'component_atol':1e-4,'component_rtol':1e-5},'passed':True},
 'function_coefficients':{str(k):v for k,v in function_coefficients.items()},
 'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
assert certificate_checked and grouping_checked and len(coeff_by_k)==N+1
(notebook_dir/'state/pgm_b4.json').write_text(json.dumps(state,indent=2,allow_nan=False))
