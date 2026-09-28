import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'feg_example_lyap.ipynb'
nb=json.loads(p.read_text(encoding='utf-8'))
index=next(i for i,c in enumerate(nb['cells']) if c['cell_type']=='markdown' and ''.join(c['source']).startswith('## Lyapunov partial sums'))
nb['cells'][index:index]=[dict(cell_type='markdown',id='b2-confirm-n8-note',metadata={},source=['### Additional certificate for rank confirmation\nAn additional complete certificate at $N=8$ uses the same retained-pair recipe and verification code as the selected $N=6$ certificate. Both dense and relaxed solves use CLARABEL defaults. The numerical checks and matching decomposition are retained together in `supplementary/N8/`; $N=6$ remains selected.']),dict(cell_type='code',id='b2-confirm-n8-values',metadata={},execution_count=None,outputs=[],source=['confirmation = json.loads((notebook_dir / "supplementary/N8/feg_b2.json").read_text())\nprint("Confirmation certificate N:",confirmation["N_verify"])\nprint("Bound:",confirmation["opt_value"],"status:",confirmation["solver_status"])\nprint("Full-coordinate checks:",confirmation["numerical_checks"]["residuals"])\nprint("Analytic full-PEP verified:",confirmation["analytic_full_pep_verified"])'])]
p.write_text(json.dumps(nb,indent=1,ensure_ascii=False),encoding='utf-8')
