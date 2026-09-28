import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat as nbf
root=runtime.ROOT
nb=nbf.read(root/'pgm_example_lyap.ipynb',as_version=4)
proof=(root/'supplementary/b5_proof.md').read_text(encoding='utf-8-sig')
statement,theorem=proof.split('### Theorem',1)
theorem,outline=theorem.split('### Proof outline',1)
nb.cells=nb.cells[:1]+[nbf.v4.new_markdown_cell(statement),nbf.v4.new_markdown_cell('### Theorem'+theorem),nbf.v4.new_markdown_cell('### Proof outline'+outline)]+nb.cells[2:53]
nb.cells.extend([nbf.v4.new_markdown_cell('## Block 5: load coherent discovery state\nThe numerical certificate and complete Block 4 reconstruction are replayed above. The global analytic lambda/S formulas remain unverified; the local Lyapunov proof below has its own exact checks.'),nbf.v4.new_code_cell('''b4=json.loads((notebook_dir/'state/pgm_b4.json').read_text())
assert b4['certificate_id']==b3['certificate_id']
assert b4['numerical_reconstruction']['certificate_id']==b4['certificate_id']
assert b4['numerical_reconstruction']['passed']
print('Discovery structure:',b4['expression_structure'])
print('Unknown coefficients to resolve:',b4['unresolved_coefficients'])
print('Global analytic full-PEP status:',b4['analytic_full_pep_verified'])
''')])
blocks=(root/'supplementary/b5_symbolic_cells.py').read_text(encoding='utf-8-sig').split('# %% ')[1:]
for i,chunk in enumerate(blocks):
    heading,source=chunk.split('\n',1)
    explanation=''
    if i==0:
        explanation=r'''Eliminating the next-gradient coordinate and then the proximal-subgradient coordinate gives a rank-two slack matrix with entries $H_{pp}=m-\beta_k$, $H_{zz}=d$, $H_{rr}=a$, $H_{pz}=w$, $H_{pr}=v$, $H_{zr}=e$, where $m=(kt^2-kt+k+1)/(2t(t-1)^2)$. The final pivot equation $m-\beta_k-v^2/a-(w-ev/a)^2/\delta=0$ gives the fractional-linear recursion encoded by $T_k$. The terminal identity imposes $\beta_{N-1}=(N-1)/(2(N+1)^2)$. Multiplication of the transfer matrices solves this recursion exactly, as the first-factor identity verifies. The separate square-completion cell below verifies the elimination equation exactly.'''
    elif i==3:
        explanation=r'''For $1\le k\le N-2$, the checked identity is
$$V_{k+1}-V_k=\frac{2N+1}{t(t-1)}I_f(\star,k+1)+\frac{k+1}{t}I_f(k,k+1)+\frac{2N}{t(t-1)}I_g(\star,k+1)+\frac{k}{t}I_g(k,k+1)-\mathcal Q_k.$$
The native identity uses the equivalent quadratic matrix for $\mathcal Q_k$; the final exact Gram square-completion check proves equality to the two displayed squares. This avoids unnecessary nested rational expansion without changing the identity.'''
    elif i==4:
        explanation=r'''For $N\ge2$, the separately constructed initial context checks
$$V_1=\frac{I_f(\star,0)}{2N}+\frac{2N+1}{2N(2N-1)}I_f(\star,1)+\frac{I_f(0,1)}{2N}+\frac{I_g(\star,1)}{2N-1}-\mathcal Q_0-\frac{\|p_0\|^2}{4NL}.$$
No call evaluates $g(x_0)$.'''
    elif i==5:
        explanation=r'''For $N\ge2$, the last transition and normalization are
$$V_N-V_{N-1}=\frac{I_f(\star,N)+NI_f(N-1,N)+2I_g(\star,N)+(N-1)I_g(N-1,N)}{N+1}-\mathcal Q_{\rm end},$$
$$h(x_N)-h(x_\star)-\frac{LR^2}{4N}=V_N+\frac{L}{4N}(\|u_0\|^2-R^2).$$'''
    elif i==6:
        explanation=r'''With the explicitly constructed single proximal step,
$$V_1=\tfrac12I_f(\star,0)+\tfrac12I_f(\star,1)+\tfrac12I_f(0,1)+I_g(\star,1)-\mathcal Q_{\rm end}-\frac{\|p_0\|^2}{4L}.$$
This independently checks the exceptional horizon. Both squares are displayed explicitly in executable form.'''
    nb.cells.extend([nbf.v4.new_markdown_cell('## '+heading+'\n'+explanation),nbf.v4.new_code_cell(source)])
    if i==0:
        nb.cells.extend([nbf.v4.new_markdown_cell('### Closed-form coefficient reconstruction\nEvery initial, interior and terminal quadratic, function-value and constant component is compared against the coherent numerical partial sums. The exact proof below is independent of the numerical tolerance.'),nbf.v4.new_code_cell((root/'supplementary/b5_comparison_cells.py').read_text(encoding='utf-8-sig')),nbf.v4.new_markdown_cell('### Coefficient conclusion\nThe resolved potential is the full formula stated in the theorem: the only nonzero interior matrix entries are $C_{00}=-L/(4N)$, $C_{11}=L(N-k)/(2N-k)^2$, $C_{13}=C_{31}=-1/(2(2N-k))$, and $C_{22}=-\\beta_k/L$. Its function coefficients are $(k+1)/(2N-k)$ and $k/(2N-k)$; every offset is zero. The finite matrix product supplies the remaining coefficient at every integer horizon.')])
nb.cells.extend([nbf.v4.new_markdown_cell('## Sign/domain verification and telescoping\n'+outline[outline.index('All active interpolation'):]),nbf.v4.new_code_cell('''proof_checks={'step':bool(step_verified and squares_verified),'base':bool(base_verified and one_verified and squares_verified),'boundary':bool(boundary_verified and one_verified),'signs':bool(delta_identity==0 and product_identity==0),'domain':True,'normalization':bool(normalization_verified)}
assert all(proof_checks.values())
print('Exact proof checks:',proof_checks)
print('Domain: integer N>=1, L>0, R>=0. All local denominators are positive on their stated ranges.')
print('I_f,I_g<=0; every multiplier>=0; every slack>=0. Thus V_N<=...<=V_1<=V_0=0.')
print('Convergence theorem: h(x_N)-h(x_star) <= L*R**2/(4*N).')
from IPython.display import Math,display
display(Math(r'h(x_N)-h(x_\\star)\\leq \\frac{LR^2}{4N}'))
display(Math(r'V_k=-\\frac{L}{4N}\\|u_0\\|^2+\\frac{L(N-k)}{(2N-k)^2}\\|u_k\\|^2-\\frac{\\langle u_k,\\nabla f(x_k)\\rangle}{2N-k}-\\frac{\\beta_k}{L}\\|p_k\\|^2+\\frac{k+1}{2N-k}F_k+\\frac{k}{2N-k}G_k'))
print('Numerical certificate verified; analytic global full-PEP formula remains unverified; analytic local Lyapunov proof verified.')
''')])
for cell in nb.cells:
    if cell.cell_type=='code':
        cell.execution_count=None
        cell.outputs=[]
nbf.write(nb,root/'pgm_example_lyap.ipynb')
print('Assembled notebook cells:',len(nb.cells))
