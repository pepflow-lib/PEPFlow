from pathlib import Path
import json,re
r=Path(chr(92)*2+'?'+chr(92)+str(Path(__file__).resolve().parent));v=r/'validation'
for name in ['b5-static-002.json','b5-static-003.json']:
 d=json.loads((v/'supplementary'/name).read_text());print(name,[(c['label'],c['returncode']) for c in d['commands']]);print('keys',d.keys())
a=json.loads((r/'own-generation-host-access-calls.json').read_text());print('access calls',len(a))
for i,c in enumerate(a):
 s=c['arguments']
 if any(w in s.lower() for w in ['appdata','_references','web','http','git ','get-content','read_text','rg ']):
  print(i,c['timestamp'],s[:850].replace('\n',' '))
