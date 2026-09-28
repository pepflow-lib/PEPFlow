import os, sys, json, hashlib, contextlib, traceback
from pathlib import Path
root=Path.cwd().resolve()
runtime=root/"review_runtime"
runtime.mkdir(exist_ok=True)
for key in ["TEMP","TMP","TMPDIR","MPLCONFIGDIR","XDG_CACHE_HOME","IPYTHONDIR","JUPYTER_RUNTIME_DIR","JUPYTER_CONFIG_DIR","PYTHONPYCACHEPREFIX"]:
    p=runtime/key.lower(); p.mkdir(exist_ok=True); os.environ[key]=str(p)
os.environ["MPLBACKEND"]="Agg"
sys.path.insert(0,str(root/"supplementary/approved"))
import numpy as np
nb=json.loads((root/"dual_feg_example_lyap.ipynb").read_text(encoding="utf-8"))
settings=json.loads((root.parent/"settings.json").read_text(encoding="utf-8-sig"))
original=Path(settings["original_submission"])
hash_errors=[p for p,h in settings["submission_hashes"].items() if hashlib.sha256((original/p).read_bytes()).hexdigest()!=h]
assert not hash_errors,hash_errors
ns={"NOTEBOOK_DIR":root,"json":json,"sys":sys,"Path":Path,"np":np}
indices=[5,7,9,10,15,17,19,21,23,24,25,26,28,30,31,33,35,37,38,42,43,46,49,52,55,58]
report={"hashes_checked":len(settings["submission_hashes"]),"hash_errors":hash_errors,"cells":[]}
with (root/"replay.log").open("w",encoding="utf-8") as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    for i in indices:
        cell=nb["cells"][i]
        print("CELL",i,cell["id"],flush=True)
        try: exec(compile("".join(cell["source"]),f"notebook cell {i}","exec"),ns)
        except Exception:
            report["cells"].append({"index":i,"id":cell["id"],"passed":False});traceback.print_exc();break
        report["cells"].append({"index":i,"id":cell["id"],"passed":True})
report["passed"]=len(report["cells"])==len(indices) and all(c["passed"] for c in report["cells"])
if report["passed"]:
    report["rank_samples"]=[{k:s[k] for k in ["N","rank_profile","coverage_residuals","identity_residuals","rank_credible"]} for s in ns["rank_samples"]]
    cert=ns["certificate"]; S=np.asarray(cert["S_matrix"])
    report["minimum_S_eigenvalue"]=float(np.linalg.eigvalsh(S).min())
    report["minimum_retained_dual"]=min(v for v in cert["named_dual_values"].values() if v is not None)
    report["proof_checks"]=ns["proof_checks"]
(root/"replay.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))

