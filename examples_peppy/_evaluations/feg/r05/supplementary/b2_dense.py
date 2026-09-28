import importlib.util
from pathlib import Path
import json

spec = importlib.util.spec_from_file_location('runtime', Path(__file__).parent / 'helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
from certificates import acquire, summarize

*_, data = acquire(6)
(runtime.ROOT / 'state/feg_dense.json').write_text(json.dumps(data, indent=2))
summarize(data)
