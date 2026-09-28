"""Exercise unchanged adapter with argparse-compatible positional ordering."""

import importlib.util
import os
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
os.environ["PEPPY_TEST_TY"] = (
    "C:/Users/Jack/AppData/Local/uv/cache/archive-v0/VWo92b0BJr6Q4_o3qIBeK/ty-0.0.82.data/scripts/ty.exe"
)
spec = importlib.util.spec_from_file_location(
    "synthetic_adapter_tests",
    root / "plugins/pepflow-workflows/tests/test_static_isolation.py",
)
assert spec is not None and spec.loader is not None
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
original = tests.adapter.main


def reordered(argv=None):
    if argv and "--" in argv:
        i = argv.index("--")
        argv = argv[1:i] + [argv[0]] + argv[i:]
    return original(argv)


tests.adapter.main = reordered
with (root / "tmp/peppy_astra_static_cli_tests.log").open("w", encoding="utf-8") as f:
    result = unittest.TextTestRunner(stream=f, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(tests)
    )
raise SystemExit(0 if result.wasSuccessful() else 1)
