import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('runtime',Path(__file__).parent/'helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import b5_math
print(b5_math.proof_checks)
