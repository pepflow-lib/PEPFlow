from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "ogm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
nb.cells.insert(
    -1,
    nbf.v4.new_markdown_cell(
        "### Additional horizon certificate\nBlock 3 requested horizon 6 for a rank comparison. The same support rule was solved afresh; its complete certificate is separate from the selected horizon-4 certificate. The existing formula search was reused and its candidates checked at the new horizon."
    ),
)
nb.cells.insert(
    -1,
    nbf.v4.new_code_cell(
        'certificate6 = json.loads((notebook_dir / "supplementary" / "b2-N6-certificate.json").read_text())\nassert certificate_digest(certificate6) == certificate6["certificate_id"]\nrevalidated6 = revalidate(certificate6)\nprint("N=6 full-coordinate residuals:", revalidated6[-1])\nprint("N=6 dense-relaxed gap:", certificate6["numerical_checks"]["residuals"]["dense_relaxed_gap"])\nprint("N=6 candidate comparisons:", certificate6["closed_form_search"]["additional_horizon_candidate_checks"])'
    ),
)
nbf.write(nb, path)
