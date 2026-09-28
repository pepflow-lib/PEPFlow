"""Execute B4 calculations and persist the verified state."""
import json
import runpy
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'supplementary/helpers'))
    from runtime import configure

    configure()
    values = runpy.run_path(str(root / 'supplementary/b4_math.py'))
    (root / 'state/ogm_b4.json').write_text(json.dumps(values['b4'], indent=2, allow_nan=False), encoding='utf-8')


if __name__ == '__main__':
    main()
