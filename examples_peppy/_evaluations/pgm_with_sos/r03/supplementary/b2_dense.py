import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import configure, NOTEBOOK_DIR
configure()
from certificates import capture, verify, save
ctx,pb,result,data=capture(6)
checks,_=verify(ctx,pb,data,data["opt_value"])
data["checks"]=checks
save(NOTEBOOK_DIR/"state/pgm_dense.json",data)
print("Dense objective",data["opt_value"], "checks",checks)
for name,v in data["named_dual_values"].items():
    print(name, v)

