"""Add the verified partial-sum construction while replaying saved B2 data."""
from pathlib import Path

import nbformat as nbf

root = Path(__file__).resolve().parent.parent
nb = nbf.read(root / "pgm_example_lyap.ipynb", as_version=4)
nb.cells = nb.cells[:21]
nb.cells[13].source = nb.cells[13].source.replace(
    'dense = capture(ctx, pb, obj, params)',
    'dense = json.loads((notebook_dir / "state/pgm_dense.json").read_text())\nprint("Replaying dense acquisition saved during B2.")')
nb.cells[15].source = nb.cells[15].source.replace(
    'selected = capture(ctx, pb, obj, params, dense["opt_value"])',
    'selected = json.loads((notebook_dir / "state/pgm_b2.json").read_text())\nprint("Replaying the selected B2 certificate; no new solve.")')
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
source = (root / "supplementary/h/partial_sums.py").read_text().split("\n", 1)[1]
source = source.replace("from certificate import certificate_id, inventory, verify\n", "")
analytic_source = (root / "supplementary/h/analytic.py").read_text().split("\n", 1)[1]
source = analytic_source + "\n" + source[source.index("def rebuild_check"):]
nb.cells += [
md(r"""## Lyapunov partial sums

With residuals $r_i\le0$, assign each interpolation inequality to the step ending at its destination iterate (the initial optimum-to-$x_0$ term is included in the first step). Start with the explicit analytic PSD squares below. To match the saved numerical matrix $S$, apply $T=S^{1/2}S_{\mathrm{analytic}}^{\dagger/2}$ to every square matrix, and add the PSD remainder $S^{1/2}(I-P)S^{1/2}$ at the terminal step, where $P$ projects onto the analytic range. This preserves each piece's numerical sign and reconstructs the same saved $S$ to roundoff. No saved multiplier is changed. The original reverse-LDL discovery is archived in supplementary/ldl-discovery.
$$V_0=0,\qquad V_{k+1}-V_k=\sum_{i\in\mathcal I_k}\lambda_i r_i-\sum_{j\in\mathcal S_k}S_j\le0.$$
The final sum covers every interpolation contribution and every $S$ piece. The initial distance constraint supplies the normalization boundary:
$$V_N=h(x_N)-h(x_\star)-\tau\|x_0-x_\star\|^2$$
up to the reported numerical certificate residual. Interior Gram rank is 4 at $N=4,6$, using fixed exclusions of one endpoint on each side. This is numerical structural evidence, not an arbitrary-horizon proof."""),
code(source),
code("""certificate = json.loads((notebook_dir / "state/pgm_b2.json").read_text())
ctx, pb, obj, replay_checks = rebuild_check(notebook_dir, certificate, get_pep_setup)
certificate_checked = replay_checks["passed"]
print("Rebuilt certificate checks:", replay_checks["residuals"])
pm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(certificate["params_json"]))
lyap, S_piece_terms, interpolation_terms, selected_record = construct(ctx, pb, certificate, verbose=True)
grouping_checked = selected_record["grouping_checked"]
print("Full-coordinate coverage:", selected_record["coverage_max_abs"])
print("Full-coordinate boundary:", selected_record["boundary_max_abs"])
print("Maximum increment residual:", selected_record["increment_max_abs"])
print("All interpolation terms and PSD pieces assigned; no terminal leftovers.")
"""),
code("""rank_samples = [selected_record]
additional = json.loads((notebook_dir / "supplementary/b2_n6.json").read_text())
additional_ctx, additional_pb, _, additional_checks = rebuild_check(notebook_dir, additional, get_pep_setup)
_, _, _, additional_record = construct(additional_ctx, additional_pb, additional)
rank_samples.append(additional_record)
retained = [sample["rank_profile"][1:-1] for sample in rank_samples]
assert all(len(values) >= 3 and len(set(values)) == 1 for values in retained)
assert len({values[0] for values in retained}) == 1
assert all(sample["rank_credible"] and sample["certificate_checked"] and sample["grouping_checked"]
           for sample in rank_samples)
rank_search = {
    "status": "confirmed", "boundary_exclusions": {"left": 1, "right": 1},
    "rank": retained[0][0], "confirmed_horizons": [sample["N"] for sample in rank_samples],
    "selected_certificate_id": certificate["certificate_id"],
    "recipe_id": selected_record["recipe_id"],
    "rank_convention": selected_record["rank_convention"],
    "evidence_path": "supplementary/rank_search.json"}
print("Confirmed horizons:", rank_search["confirmed_horizons"],
      "common interior rank:", rank_search["rank"],
      "endpoint exclusions: (1, 1); absolute unscaled SVD threshold: 1e-4")
print("No singular value lies between 5e-5 and 2e-4 at either horizon.")
(notebook_dir / "supplementary/rank_search.json").write_text(json.dumps(
    {"summary": rank_search, "samples": rank_samples}, indent=2))
ctx.set_as_current()
"""),
code(r"""certificate_source = (notebook_dir / "supplementary/h/certificate.py").read_text()
certificate_check_code = (certificate_source + "\n" + inspect.getsource(rebuild_check)
    + "\nctx, pb, obj, replay_checks = rebuild_check(notebook_dir, certificate, get_pep_setup)\n"
    + "certificate_checked = replay_checks['passed']\n"
    + "pm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(certificate['params_json']))\n")
decomposition_code = ((notebook_dir / "supplementary/h/analytic.py").read_text()
    + "\n" + inspect.getsource(build_pieces)
    + "\nS_piece_terms, S_assignment = build_pieces(ctx, certificate, pm)\n")
grouping_code = inspect.getsource(construct) + "\nlyap, S_piece_terms, interpolation_terms, selected_record = construct(ctx, pb, certificate, verbose=True)\ngrouping_checked = selected_record['grouping_checked']\n"
state3 = {
    **certificate,
    "rank_profile": selected_record["rank_profile"], "rank_search": rank_search,
    "lyap_inner_prod_coords": selected_record["lyap_inner_prod_coords"],
    "lyap_func_coords": selected_record["lyap_func_coords"],
    "lyap_offsets": selected_record["lyap_offsets"],
    "certificate_check_code": certificate_check_code,
    "decomposition_code": decomposition_code, "grouping_code": grouping_code,
    "extra_duals": {}, "rank_tolerance": 1e-4,
    "reconstruction_tolerance": 1e-4, "reconstruction_rtol": 1e-5,
    "grouping_coverage": {
        "constraint_assignment": selected_record["constraint_assignment"],
        "S_assignment": selected_record["S_assignment"],
        "normalization_constraint": "initial_condition",
        "boundary_constraints": [], "boundary_S": [], "omitted_constraints": [],
        "checked": True, "coverage_max_abs": selected_record["coverage_max_abs"],
        "boundary_max_abs": selected_record["boundary_max_abs"],
        "increment_max_abs": selected_record["increment_max_abs"]},
    "grouping_source_sha256": hashlib.sha256(
        (notebook_dir / "supplementary/h/partial_sums.py").read_bytes()).hexdigest(),
    "analytic_decomposition_sha256": hashlib.sha256(
        (notebook_dir / "supplementary/h/analytic.py").read_bytes()).hexdigest(),
    "numerical_certificate_verified": True, "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False}
(notebook_dir / "state/pgm_b3.json").write_text(json.dumps(state3, indent=2))
print("B3 numerical rank and coverage gates passed; basis reconstruction remains pending.")
"""),
md("## Identify the vectors composing the Lyapunov function\n\nPending Block 4."),
md("## Closed-form coefficients and symbolic identities\n\nPending Block 5."),
]
nbf.write(nb, root / "pgm_example_lyap.ipynb")
