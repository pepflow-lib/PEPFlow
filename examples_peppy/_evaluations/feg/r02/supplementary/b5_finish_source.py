import json
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'feg_example_lyap.ipynb'
nb=json.loads(p.read_text(encoding='utf-8'))
for c in nb['cells']:
    s=''.join(c['source'])
    if c['cell_type']=='code' and s.startswith('def exact_coefficients'):
        s += '\nG_symbol,H_symbol=sp.symbols("G H",real=True)\nV_display=2*k_symbol**2/N_symbol**2*G_symbol+4*k_symbol*L_symbol/N_symbol**2*H_symbol\nprint("V_k with G=||A(x_k)||^2 and H=<A(x_k),x_k-x_0>:",V_display)\nprint("LaTeX:",sp.latex(V_display))\n'
        c['source']=s
    if c['cell_type']=='markdown':
        def normalize(match):
            fragment=match.group(0).replace('x_\\star','x_{\\star}')
            fragment=re.sub(r'_([A-Za-z0-9])(?![A-Za-z0-9])',r'_{\1}',fragment)
            return fragment
        c['source']=re.sub(r'\$\$.*?\$\$|\$[^$]*\$',normalize,s,flags=re.S)
p.write_text(json.dumps(nb,indent=1,ensure_ascii=False),encoding='utf-8')
