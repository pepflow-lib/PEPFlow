import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import nbformat
root=runtime.ATTEMPT
book=nbformat.read(root/'pgm_example_lyap.ipynb',as_version=4)
check = '''import json
import hashlib
from pathlib import Path
import numpy as np
import sympy as sp
import pepflow as pf
from pgm_setup import get_pep_setup, f, g, L
from candidates import aid_pieces, square_sum, multiplier_candidate

N = certificate["N_verify"]
b2 = certificate
'''+book.cells[11].source+'''
# Independently check the original saved S, beyond its candidate reconstruction.
basis = ctx_b2.basis_vectors()
S_scalar = sum((float(S_saved[i,j])*basis[i]*basis[j]
                for i,j in np.ndindex(S_saved.shape)), pf.Scalar.zero())
saved_identity = pm.eval_scalar(pb_b2.performance_metric - b2["opt_value"] - weighted + S_scalar)
assert all(maxabs(v) <= 1e-5 for v in (saved_identity.inner_prod_coords, saved_identity.func_coords, saved_identity.offset))
certificate_checked = True
'''
(root/'supplementary/b3_certificate_check.py').write_text(check)
