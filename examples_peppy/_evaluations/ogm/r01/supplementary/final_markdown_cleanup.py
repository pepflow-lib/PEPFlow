import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "ogm_example_lyap.ipynb"
nb = json.loads(path.read_text(encoding="utf-8"))


def code_digest():
    return hashlib.sha256(
        "\n".join(
            "".join(cell["source"])
            for cell in nb["cells"]
            if cell["cell_type"] == "code"
        ).encode()
    ).hexdigest()


before = code_digest()
nb["cells"][12]["source"] = [
    "The B1 sweep suggested $f(x_{N})-f(x_{\\star})\\leq LR^{2}/(2\\theta_{N}^{2})$. The following sections preserve the discovery trail; the exact proof at the end establishes this bound for every admissible horizon."
]
nb["cells"][36]["source"] = [
    "At the B4 discovery stage, the diagonal coefficient pattern below was a numerical candidate checked against every extracted matrix and function coefficient. The final symbolic section establishes the formulas analytically."
]
after = code_digest()
assert before == after
for cell in nb["cells"]:
    if cell["cell_type"] == "markdown":
        source = "".join(cell["source"])
        assert not any(ch in source for ch in ("\t", "\r", "\f", "\x08"))
        assert source.count("$") % 2 == 0
path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
(root / "supplementary/b5-final-markdown-evidence.json").write_text(
    json.dumps(
        {
            "edit": "Updated historical B1/B4 status prose after final proof",
            "code_sha256_before": before,
            "code_sha256_after": after,
            "code_unchanged": True,
            "presentation_policy": "evaluation-ancillary-v1",
            "rendered_review": "not performed by instruction; source delimiter/escape checks passed",
        },
        indent=2,
    )
)
print("Final prose updated; executable source unchanged.")
