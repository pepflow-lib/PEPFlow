from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "supplementary/finalize_b2.py").read_text(encoding="utf-8-sig")
source = source.replace(
    'dense = json.loads((ROOT / "state/dual_feg_dense.json").read_text())',
    'b1["N_verify"] = 8\ndense = capture(8)\n(ROOT / "supplementary/dense_N8.json").write_text(json.dumps(dense, indent=2))',
)
source = source.replace(
    'prior = json.loads((ROOT / "supplementary/sparse_candidate_2.json").read_text())\ns = capture(6, prior["relaxed_constraints"])',
    """N_target = 8
keep = {"initial_condition", f"A monotone:x_{N_target},x_star"}
keep |= {f"A monotone:x_{N_target},y_{k}" for k in range(N_target-1)}
keep |= {f"A Lipschitz:x_{k},y_{k}" for k in range(N_target-1)}
keep.add(f"A Lipschitz:x_{N_target-1},x_{N_target}")
s = capture(N_target, [name for name in dense["named_dual_values"] if name not in keep])""",
)
source = source.replace(
    'for name in ["dual_feg_b2.json", "dual_feg_relaxed.json"]:\n    (ROOT / "state" / name).write_text(json.dumps(s, indent=2, allow_nan=False))',
    '(ROOT / "supplementary/certificate_N8.json").write_text(json.dumps(s, indent=2, allow_nan=False))',
)
(ROOT / "supplementary/acquire_N8.py").write_text(source)
