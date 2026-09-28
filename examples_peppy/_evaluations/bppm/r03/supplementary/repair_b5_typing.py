from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
path=root/'bppm_example_lyap.ipynb'
book=json.loads(path.read_text())
for index,name in ((40,'common'),(43,'step'),(46,'base'),(49,'boundary')):
    book['cells'][index]['source']=(root/f'supplementary/b5_{name}.py').read_text(encoding='utf-8-sig').splitlines(keepends=True)
path.write_text(json.dumps(book,indent=1),encoding='utf-8')
