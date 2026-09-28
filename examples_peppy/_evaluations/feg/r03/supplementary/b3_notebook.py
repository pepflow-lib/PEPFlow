import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import hashlib
import nbformat as nbf
from nbclient import NotebookClient
root=runtime.ROOT
path=root/'feg_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
b3=json.loads((root/'state/feg_b3.json').read_text())
start=next(i for i,c in enumerate(nb.cells) if c.source.startswith('## Partial-sum'))
end=next(i for i,c in enumerate(nb.cells) if c.source.startswith('## Identify'))
md=nbf.v4.new_markdown_cell
code=nbf.v4.new_code_cell
cells=[md(r'''## Partial-sum Lyapunov construction and rank profile
Write $I_k^{\rm Lip}=\|g_{k+1}-A(x_{k+1/2})\|^2-L^2\|x_{k+1}-x_{k+1/2}\|^2\le0$ and $I_k^{\rm Mon}=-\langle g_{k+1}-g_k,x_{k+1}-x_k\rangle\le0$. Using the saved numerical multipliers, define $V_0=0$ and
$$V_{k+1}-V_k=\lambda_k^{\rm Lip}I_k^{\rm Lip}+\lambda_k^{\rm Mon}I_k^{\rm Mon},$$
with no monotonicity term when $k=0$. Every coefficient is nonnegative, so $V_{k+1}\le V_k$ at the numerical certificate level. The terminal zero-point monotonicity inequality and the full PSD remainder are held for the boundary argument. No terms are omitted.
At both $N=4$ and $N=6$, excluding only $V_0$ and $V_N$ gives constant rank two, with at least three retained indices. Rank uses absolute tolerance $10^{-4}$ in the original coordinates with no scaling; all retained singular values are well separated from the threshold. This is finite-sample structure, not an arbitrary-horizon proof.'''),code('''certificate = json.loads((notebook_dir/"state/feg_b2.json").read_text())
N_int = certificate["N_verify"]
N = sp.S(N_int)
params_sp = {key:sp.S(value) for key,value in json.loads(certificate["params_json"]).items()}
REPO_ROOT = repo_root
ctx,pb,obj = get_pep_setup(N,params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
ctx.set_as_current()'''),code(b3['certificate_check_code']),code(b3['decomposition_code']),code(b3['grouping_code']),code('''rank_evidence = json.loads((notebook_dir/"supplementary/rank_search.json").read_text())
summary = rank_evidence["summary"]
assert summary["selected_certificate_id"] == certificate["certificate_id"]
assert summary["boundary_exclusions"] == {"left":1,"right":1}
for sample in rank_evidence["samples"]:
    kept = sample["rank_profile"][1:sample["N"]]
    assert len(kept)>=3 and set(kept)=={2}
    assert sample["certificate_checked"] and sample["grouping_checked"] and sample["rank_credible"]
    print("Confirmed horizon:",sample["N"],"retained indices:",list(range(1,sample["N"])),"common rank:",2)
print("Absolute rank tolerance:",rank_tolerance,"scaling: none")
print("Terminal leftovers: one zero-point monotonicity inequality and one full PSD block; no omissions.")
print("Analytic full-PEP and Lyapunov proofs remain unresolved.")''')]
nb.cells[start:end]=cells
nbf.write(nb,path)
NotebookClient(nb,timeout=120,kernel_name='feg-private',resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb,path)
for cell in nb.cells:
    if cell.cell_type=='markdown':
        assert '\\(' not in cell.source and '\\[' not in cell.source
        assert all(ord(ch)>=32 or ch in '\n\t' for ch in cell.source)
    assert all(out.output_type!='error' for out in cell.get('outputs',[]))
check=root/'supplementary/feg_example_lyap_checklist.md'
lines=check.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'):lines[i]='Last reviewed block: B3'
    if line.startswith('SHA-256:'):lines[i]='SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()
    if line.startswith('| 9 |'):lines[i]=f'| 9 | partial-sum Lyapunov construction and rank profile | verified | {start}-{start+5} | Certificate replay, exact executed grouping, complete coverage/sign/step checks; rank two confirmed at N4 and N6 with fixed exclusions (1,1). |'
    for item,heading in [(10,'## Identify'),(11,'## Coefficient'),(12,'## Symbolic')]:
        if line.startswith(f'| {item} |'):
            parts=line.split('|');parts[4]=' '+str(next(j for j,c in enumerate(nb.cells) if c.source.startswith(heading)))+' ';lines[i]='|'.join(parts)
check.write_text('\n'.join(lines)+'\n')
print('B3 notebook executed:',len(nb.cells),'cells')
