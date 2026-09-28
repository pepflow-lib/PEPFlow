"""Partial-sum observation at the selected existing certificate."""
import json
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'supplementary/helpers'))
    from runtime import configure

    configure()
    from partial_sums import construct

    certificate = json.loads((root / 'state/ogm_b2.json').read_text())
    observation = construct(certificate)
    destination = root / f"supplementary/b3-observation-N{observation['N']}.json"
    destination.write_text(json.dumps(observation, indent=2), encoding='utf-8')
    print('Coverage residual:', observation['coverage_max_abs'])
    print('Singular values:', observation['singular_values'])


if __name__ == '__main__':
    main()
