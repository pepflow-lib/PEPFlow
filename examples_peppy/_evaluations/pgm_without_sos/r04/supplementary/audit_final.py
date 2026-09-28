import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import json

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]
import runtime

root = runtime.ATTEMPT
path = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
streams = []
executed = []
for i, cell in enumerate(nb.cells):
    if cell.cell_type == "markdown":
        assert cell.source.count("$") % 2 == 0, (i, "unbalanced dollar delimiters")
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(c) < 32 and c not in "\n\t" for c in cell.source)
        print(i, "MARKDOWN", cell.source.splitlines()[0])
    else:
        assert cell.execution_count is not None, (i, "not executed")
        assert not any(
            output.output_type == "error" for output in cell.get("outputs", [])
        )
        executed.append(i)
        output_text = "".join(
            o.get("text", "")
            for o in cell.get("outputs", [])
            if o.output_type == "stream"
        )
        streams.append(output_text)
        mime_types = sorted(
            {mime for o in cell.get("outputs", []) for mime in o.get("data", {})}
        )
        print(
            i,
            "CODE",
            cell.execution_count,
            "MIME",
            mime_types,
            "markers",
            [
                line
                for line in output_text.splitlines()
                if any(
                    key in line
                    for key in (
                        "exact zero",
                        "complete reconstruction",
                        "rank V_",
                        "Confirmed interior",
                        "Maximum discrepancy",
                        "reconstruction residual",
                        "Signs:",
                        "Telescoping:",
                    )
                )
            ],
        )
all_stream = "\n".join(streams)
for label in (
    "Interior step",
    "Base N>=2",
    "Terminal step N>=2",
    "Terminal normalization",
    "Exceptional N=1",
):
    assert (
        label + " : exact zero in Gram, function and offset coordinates" in all_stream
    ), label
assert any(
    "image/png" in o.get("data", {}) for c in nb.cells for o in c.get("outputs", [])
)
assert "Solved coefficient equation:" in all_stream
assert "Exact transfer-ratio identity: zero" in all_stream
assert "Confirmed interior rank: 4 horizons: [4, 6]" in all_stream
assert "All indices reconstructed." in all_stream
assert "Telescoping: V_N <= V_0 = 0" in all_stream
static = json.loads((root / "supplementary/b5-static-002.json").read_text())
execution = json.loads((root / "supplementary/b5-final-execution.json").read_text())
assert static["status"] == "passed"
assert execution["returncode"] == 0
record = dict(
    notebook="pgm_example_lyap.ipynb",
    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    code_cell_count=len(executed),
    executed_indices=executed,
    all_code_cells_executed=True,
    proof_markers_verified=True,
    comparison_plot_present=True,
    markdown_source_checks_passed=True,
    presentation_policy="evaluation-ancillary-v1",
    rendered_review_performed=False,
    static_evidence="supplementary/b5-static-002.json",
    execution_evidence="supplementary/b5-final-execution.json",
)
(root / "supplementary/final-notebook-audit.json").write_text(
    json.dumps(record, indent=2)
)
print("Audit passed; notebook SHA256:", record["sha256"])
