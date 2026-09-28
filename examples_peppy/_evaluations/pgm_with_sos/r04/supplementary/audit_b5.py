from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat
import json

path=runtime.ROOT/'pgm_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
for c in nb.cells:
    if c.cell_type=='markdown':
        c.source=c.source.replace('optimal_{i}naccurate','optimal_inaccurate')
        if c.source.startswith('### Theorem'):
            c.source=c.source.replace('write $a_{i}=', 'write $f_{i}=f(x_{i})$, $g_{i}=g(x_{i})$, $h_{i}=f_{i}+g_{i}$, $a_{i}=')
        assert '\\(' not in c.source and '\\[' not in c.source
        assert not any(ord(v)<32 and v not in '\n\t' for v in c.source)
        assert '\\\\' not in c.source
    else:
        assert c.execution_count is not None
        assert all(o.output_type!='error' for o in c.outputs)
nbformat.write(nb,path)
for i,c in enumerate(nb.cells):
    if c.cell_type=='markdown':
        print(i,'MD',c.source.split('\n')[0])
    else:
        streams=''.join(o.get('text','') for o in c.outputs if o.output_type=='stream')
        displays=[list(o.get('data',{})) for o in c.outputs if o.output_type=='display_data']
        print(json.dumps({'cell':i,'execution_count':c.execution_count,'stream_tail':streams[-320:],'display_types':displays}))
