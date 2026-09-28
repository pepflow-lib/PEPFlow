import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = Path((ROOT / 'tmp/current_peppy_posthoc.txt').read_text())
settings = json.loads((P / 'settings.json').read_text())
aid = sys.argv[1]
item = settings['reviews'][aid]
assert item['status'] == 'prepared'
now = dt.datetime.now(dt.timezone.utc)
item.update(status='running', dispatched_at=now.isoformat(), deadline=(now + dt.timedelta(seconds=7200)).isoformat())
R = Path(item['directory'])
text = f'''Post hoc mathematical re-evaluation of {aid}. Use GPT-6 Astra, medium reasoning. Dispatch {item['dispatched_at']}; deadline {item['deadline']}; 7200 seconds, no token cap. No generation or proof repair. All original generation has stopped.

Read own input.md, rubric.md, historical-review.json, submission-hashes.json, submitted generic skills and actual submitted proof. The frozen rubric's mathematical criteria and exact target remain unchanged. USER OVERRIDE: generic dependency-path/launcher and notebook-display issues are operational, never a reason to suppress mathematical verification or declare mathematical FAIL. Repair the validation execution environment and continue. Do not adopt historical access exclusion as a mathematical finding. Actual prohibited target mathematical exposure must be evidenced and reported separately. Instruction-only isolation is not proof of contamination or absence of exposure.

Read only this review directory and own original submission {item['original_submission']}; generic installed dependencies and stdlib may be used for validation. No other attempts, external mathematical sources, original paper proofs, history, or controller context. No subagents. Original submission and historical review are read-only. Execute ONLY own validation copy {R / 'validation'}, inspect and redirect ALL absolute writes/state/cache/temp/helper locations before execution. Prefer pinned C:/Users/Jack/Documents/GitHub/PEPFlow/.venv/Scripts/python.exe -I -B, direct -m nbconvert if used, with explicit own helper/framework paths. Windows extended paths or an owned short runtime path inside this review directory may resolve path length errors. No rendering is needed.

Complete missing verification of the actual submitted mathematical content: algorithm/scope, fully defined coefficients and potential, general symbolic step, signs/domains, initial and terminal links, N=1 and other exceptions, exact rate/normalization. Check existing B1-B4 evidence without rerunning proof discovery or parameter search; saved certificates may be replayed. Do not invent a missing argument or repair mathematical expressions. Execution-only changes (path rewrites, symbolic display fixes, omitting plot/display calls) are allowed only in validation copies, logged with exact before/after and why proof semantics are unchanged. A real proof gap may be FAIL; inconclusive verification is REVIEW; operational interruption or missing verification is not mathematical FAIL. Do not assume PASS.

Write {R / 'review.json'} with attempt_id, mathematical_verdict (PASS/FAIL/REVIEW/NOT_EVALUATED), mathematical_reason, submitted_theorem, target_scope_comparison, verification_method (replayed vs inspected), mathematical_evidence_refs, checks (name,status,observed_result,evidence_ref), blocks B1-B5 (block_id, mathematical_status, delivery_status, reason,evidence_refs), original_delivery_status and reason, posthoc_validation_execution_status, access_findings (generic_operational_incidents, prohibited_mathematical_exposure observed/not_established/unresolved with evidence, independence_eligible, limitations), execution_adjustments (or reference to a detailed adjustment log), review_started_at, review_stopped_at, limitations. Evidence refs should be relative to this review directory or absolute own-original paths. Record fresh validation separately; do not claim original delivery completed retroactively. Preserve failed validation evidence and any repairs. Verify original hashes before closing. Return a concise completion notice.
'''
(R / 'instructions.md').write_text(text, encoding='utf-8')
(P / 'settings.json').write_text(json.dumps(settings, indent=2))
print(R / 'instructions.md')
