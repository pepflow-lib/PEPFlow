"""Insert and execute only the B2 additional-horizon verification."""

from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
dest = root / "bppm_example_lyap.ipynb"
nb = nbf.read(dest, as_version=4)
idx = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Lyapunov partial sums")
)
cells = [
    nbf.v4.new_markdown_cell(
        "### Additional horizon certificate (B2 revisit)\n\nA fresh dense and sparse solve at N=6 used the same setup, normalization and relaxation recipe. The complete N=6 certificate is separate from the selected N=4 certificate. The following cell rechecks its full numerical identity before B3 uses it. No new rank observation is made here."
    ),
    nbf.v4.new_code_cell(
        "b2_n6 = json.loads((notebook_dir / 'supplementary/bppm_N6_b2.json').read_text())\nassert certificate_id(b2_n6) == b2_n6['certificate_id']\nfor path, expected in b2_n6['certificate_provenance']['source_hashes'].items():\n    assert hashlib.sha256((notebook_dir / path).read_bytes()).hexdigest() == expected\nctx6, pb6, obj6 = get_pep_setup(6, params)\npb6.set_relaxed_constraints(b2_n6['relaxed_constraints'])\nchecks6, residual6 = verify_certificate(ctx6, pb6, params, b2_n6, b2_n6['dense_opt_value'])\nassert checks6['passed']\nprint('N=6 complete-certificate residuals:', checks6['residuals'])\nprint('N=6 candidate multiplier discrepancy:', b2_n6['candidate_lambda_max_error'])\nprint('N=6 candidate S discrepancy:', b2_n6['candidate_S_max_error'])\nctx.set_as_current()"
    ),
]
nb.cells[idx:idx] = cells
nbf.write(nb, dest)
print("Inserted B2 N=6 verification before B3.")
