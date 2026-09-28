"""Apply the final audit's explicit matrix display and exact coefficient code."""

from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "ogm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
for cell in nb.cells:
    if cell.cell_type == "code" and cell.source.startswith(
        "ctx, pb, obj, pm, checked, checks = revalidate(certificate)"
    ):
        cell.source = cell.source.replace(
            'S = np.asarray(certificate["S_matrix"])',
            'S = np.asarray(certificate["S_matrix"])\nprint("Selected numerical S matrix:")\npf.pprint_labeled_matrix(pf.MatrixWithNames(S,certificate["S_row_names"],certificate["S_col_names"]))',
        )
    if cell.cell_type == "code" and cell.source.startswith(
        "def closed_form_coefficients("
    ):
        cell.source = (ROOT / "supplementary" / "b5_formula_cells.py").read_text()
    if cell.cell_type == "markdown" and cell.source.startswith(
        "## Initial formulas and numerical decomposition"
    ):
        cell.source = cell.source.replace(
            "These are numerical candidates.",
            "At the B2 discovery stage these were numerical candidates.",
        ).replace(
            "No analytic full-PEP identity has yet been proved.",
            "The later B5 section proves their analytic validity; this section preserves the original numerical comparison.",
        )
    if cell.cell_type == "markdown" and cell.source.startswith(
        "The observations suggest"
    ):
        cell.source = cell.source.replace(
            "The observations suggest", "The B1 observations suggested"
        ).replace(
            "Subsequent blocks will construct the certificate and Lyapunov proof.",
            "The subsequent sections record the certificate and Lyapunov proof that establish it.",
        )
nbf.write(nb, path)
