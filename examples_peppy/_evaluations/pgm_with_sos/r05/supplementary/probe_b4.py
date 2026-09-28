from pathlib import Path
import importlib
import json

ROOT = Path(__file__).resolve().parents[1]
exec(compile((ROOT/'supplementary'/'run_b1.py').read_text().split('results = []')[0],'bootstrap','exec'))
setup = importlib.import_module('pgm_setup')
notebook_dir=ROOT
get_pep_setup=setup.get_pep_setup
f,g,L=setup.f,setup.g,setup.L
exec(compile((ROOT/'supplementary'/'b4_construct.py').read_text(),'B4-construction','exec'))
(ROOT/'supplementary'/'b4-basis-probe.json').write_text(json.dumps(dict(
    coeff_by_k={str(k):C.tolist() for k,C in coeff_by_k.items()},
    residuals=coefficient_residuals,independence=independence,
    sparse_labels={str(k):[candidate_labels[id(v)] for v in vs] for k,vs in sparse_basis_by_k.items()}),indent=2))
