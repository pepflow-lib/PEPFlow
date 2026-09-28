import json,re
from pathlib import Path
rows=json.loads(Path('../own-generation-host-access-calls.json').read_text(encoding='utf-8'))
print('CALLS',len(rows))
for idx,row in enumerate(rows):
    arg=row.get('arguments','')
    if isinstance(arg,dict): arg=json.dumps(arg)
    # Show tool calls with surrounding script omitted after 260 chars; separate absolute targets below.
    print(idx,row['name'],arg[:230].replace('\n',' '))
paths=set()
for row in rows:
    arg=str(row.get('arguments','')).replace('\\\\','/')
    for m in re.findall(r'C:[/\\][^\"\n\r]+',arg):
        if '20260923T140754Z_paper5_pgm_sos_6x5_isolation1/pgm_with_sos/r03' not in m and '20260923T140754Z_paper5_pgm_sos_6x5_isolation1\\pgm_with_sos\\r03' not in m:
            paths.add(m[:350])
print('EXTERNAL ABSOLUTE PATH CANDIDATES',*sorted(paths),sep='\n')
