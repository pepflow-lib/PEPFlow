from pathlib import Path
import json,re
root=Path(chr(92)*2+"?"+chr(92)+str(Path(__file__).resolve().parent))
v=root/'validation'
for p in (v/'supplementary/approved/plugins').rglob('*.md'):
 if p.name=='SKILL.md' or p.name=='workflow.md':
  print('\nFILE',p.relative_to(v)); print(p.read_text(encoding='utf-8') if p.name=='SKILL.md' else '\n'.join(x for x in p.read_text(encoding='utf-8').splitlines() if re.search(r'tol|1e-|threshold|reconstruct|span|identity|rank',x,re.I)))
nb=json.loads((v/'feg_example_lyap.ipynb').read_text(encoding='utf-8'))
for c in nb['cells']:
 if c['cell_type']=='code':
  s=''.join(c['source'])
  if re.search(r'write|save|exec\(|[A-Z]:[/\\]|open\(|solve\(',s): print('AUDIT CELL',c['id'],s)
for f in ['state/feg_b1.json','state/feg_b4.json','supplementary/b3-rank-N6.json','supplementary/b4-complete-output.txt']:
 p=v/f
 if p.exists():
  if p.suffix=='.json':
   d=json.loads(p.read_text()); print('KEYS',f,list(d)); print('EVIDENCE',json.dumps({k:x for k,x in d.items() if any(w in k for w in ['sweep','search','residual','numerical','rank','tolerance'])})[:9000])
  else: print(p.read_text()[-5000:])

