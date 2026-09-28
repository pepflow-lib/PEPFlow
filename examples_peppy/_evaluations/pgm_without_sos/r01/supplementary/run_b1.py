"""B1 sweep; no certificate or later-block exploration."""
import json
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    sys.path[:0] = [str(root / "supplementary" / "approved"),
                    str(root / "supplementary" / "h"), str(root)]
    from runtime import configure
    configure()
    from runtime import solve_setup
    from pgm_setup import get_pep_setup
    
    results = []
    for N in range(1, 8):
        ctx, pb, _ = get_pep_setup(N, {"L": 1, "R": 1})
        result, metadata = solve_setup(ctx, pb, {"L": 1, "R": 1})
        row = {"N": N, "opt_value": float(result.opt_value), **metadata}
        results.append(row)
        print(json.dumps(row), flush=True)
    (root / "supplementary" / "sweep.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    
    

if __name__ == "__main__":
    main()

