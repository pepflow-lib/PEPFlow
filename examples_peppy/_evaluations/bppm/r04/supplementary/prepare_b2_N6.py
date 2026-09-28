from pathlib import Path

root = Path(__file__).resolve().parents[1]
s = (root / "supplementary/run_b2_selected.py").read_text(encoding="utf-8-sig")
s = s.replace(
    "dense = json.loads((root/'state/bppm_dense.json').read_text())",
    "_, _, _, dense = solve_capture(6, {'alpha':1,'R':1}, [], root)\n(root/'supplementary/bppm_N6_dense.json').write_text(json.dumps(dense,indent=2))",
)
s = s.replace("N = b1['N_verify']", "N = 6")
s = s.replace(
    "root/'state/bppm_constraints.json'",
    "root/'supplementary/bppm_N6_constraints.json'",
)
s = s.replace(
    "for name in ('bppm_b2.json','bppm_relaxed.json'):\n    (root/'state'/name).write_text(json.dumps(state,indent=2,allow_nan=False))",
    "(root/'supplementary/bppm_N6_b2.json').write_text(json.dumps(state,indent=2,allow_nan=False))",
)
(root / "supplementary/run_b2_N6.py").write_text(s)
