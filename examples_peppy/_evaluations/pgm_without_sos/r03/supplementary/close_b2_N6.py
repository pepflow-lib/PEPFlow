import json
import hashlib
from pathlib import Path
root=Path.cwd()
sample=json.loads((root/'supplementary/pgm_b2_N6.json').read_text())
print(json.dumps(sample['numerical_checks'],indent=2))
book_path=root/'pgm_example_lyap.ipynb'
book=json.loads(book_path.read_text())
notes='\n\nAdditional-horizon acquisition for B3: the separate $N=6$ sparse certificate is optimal and passed complete numerical checks. The dense comparison returned `optimal_inaccurate`, preserved explicitly; the dense/sparse objective difference is '+str(sample['numerical_checks']['residuals']['dense_relaxed_gap'])+'. The selected main certificate remains $N=4$. The complete additional sample is preserved in `supplementary/pgm_b2_N6.json`; its own multiplier and remainder data are kept together. Cross-horizon grouping has not yet been performed.\n'
book['cells'][8]['source']=''.join(book['cells'][8]['source'])+notes
book_path.write_text(json.dumps(book,indent=1))
p=root/'supplementary/pgm_example_lyap_checklist.md'
s=p.read_text()
s='\n'.join('SHA-256: '+hashlib.sha256(book_path.read_bytes()).hexdigest() if line.startswith('SHA-256:') else line for line in s.splitlines())
p.write_text(s+'\nAdditional N6 acquisition: notebook cell 8 records status; numerical check output preserved in supplementary/b2-N6-check-output.txt.\n')
record={'current_block':'B2','completion_status':'complete_additional_horizon','next_block':'B3','entry_exit_reason':'N6 complete optimal sparse certificate acquired and numerically verified; selected N4 retained','run_status':'awaiting_same_session_continuation','sample_path':'supplementary/pgm_b2_N6.json','dense_status':'optimal_inaccurate','selected_sample_status':'optimal','unresolved_work':'Cross-horizon grouping/rank confirmation; B4/B5 analytic Lyapunov proof','access_control':'instruction_only','prohibited_material_observed':False,'consulted_sources':['own previously generated acquisition and validation code','approved framework imports already allowlisted','own saved certificates']}
(root/'supplementary/b2-N6-handoff.json').write_text(json.dumps(record,indent=2))
