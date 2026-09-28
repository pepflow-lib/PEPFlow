"""Audit the executed final notebook and update the single twelve-item checklist."""
import hashlib
import json
from pathlib import Path

import nbformat

root = Path(__file__).resolve().parents[1]
path = root / 'dual_feg_example_lyap.ipynb'
nb = nbformat.read(path, as_version=4)
code_before = hashlib.sha256('\n'.join(c.source for c in nb.cells if c.cell_type == 'code').encode()).hexdigest()
for cell in nb.cells:
    if cell.id == 'b1-09':
        cell.source = cell.source.replace('The proof is pending.', 'The exact proof appears in the symbolic sections below.')
    if cell.id == 'b2-02':
        cell.source = cell.source.replace('Analytic full-PEP and Lyapunov proof statuses remain false.', 'At this discovery stage both analytic statuses were unverified. The final local Lyapunov proof is established below; the global full-PEP formula remains a numerical candidate.')
code_after = hashlib.sha256('\n'.join(c.source for c in nb.cells if c.cell_type == 'code').encode()).hexdigest()
assert code_before == code_after
for cell in nb.cells:
    if cell.cell_type == 'code':
        assert cell.execution_count is not None
        assert not any(o.output_type == 'error' for o in cell.outputs)
    else:
        assert not any(c in cell.source for c in ('\x0c', '\r', '\x08'))
        assert '\\(' not in cell.source and '\\[' not in cell.source
        assert cell.source.count('$$') % 2 == 0
by_id = {cell.id: cell for cell in nb.cells}
def streams(cell_id):
    return ''.join(out.get('text', '') for out in by_id[cell_id].get('outputs', []) if out.output_type == 'stream')

assert any('image/png' in out.get('data', {}) for out in by_id['b1-10'].outputs)
assert 'sparse basis:' in streams('b4-05') and 'zero coefficients:' in streams('b4-05')
assert 'All required indices' in streams('b4-11')
assert 'Confirmed interior rank:' in streams('b3-02')
for cell_id in ('b5-04', 'b5-07', 'b5-10', 'b5-13'):
    assert 'all components exactly zero: True' in streams(cell_id)
assert 'All required multipliers are positive' in streams('b5-15')
assert by_id['b5-top-00'].source == '## Proof Statement'
assert 'V_{k}' in by_id['b5-top-01'].source and 'V_{k+1}-V_{k}' in by_id['b5-top-02'].source
nbformat.write(nb, path)
checksum = hashlib.sha256(path.read_bytes()).hexdigest()
checkpath = root / 'supplementary/dual_feg_example_lyap_checklist.md'
lines = checkpath.read_text().splitlines()
updates = {
    1: ('b1-00', 'Problem, all assumptions, metric and actual update equations inspected.'),
    2: ('b5-top-00 through b5-top-02', 'Separate proof statement, theorem with exact potential, and self-contained proof outline including every residual and boundary term.'),
    3: ('b1-02,b1-03', 'Fresh kernel imported the approved framework; final static checks passed.'),
    4: ('b1-05', 'Monotone Lipschitz operator and symbolic parameters defined.'),
    5: ('b1-07,b1-08', 'Visible actual context builder and initial/metric setup executed.'),
    6: ('b1-09,b1-10', 'Seven optimal values, candidate comparison, and embedded matplotlib plot retained.'),
    7: ('b2-00,b2-01,b2n8-00,b2n8-01', 'Dense and two sparsity trials summarized; coherent N=6 and N=8 certificates replayed.'),
    8: ('b2-02,b2-03,b2n8-01', 'Initial closed-form search, full numerical identity, labeled S and residual matrices, LDL reconstruction, and explicit global formula status.'),
    9: ('b3-00 through b3-02', 'Visible actual partial-sum loop, all-coordinate coverage and PSD signs, ranks and fixed-exclusion confirmation at N=6,8.'),
    10: ('b4-00 through b4-07', 'Deduplicated candidate scan, actual anchored sparse search and per-k outputs; uniform basis independently reconstructed.'),
    11: ('b4-08 through b4-12,b5-00,b5-01', 'Every-index numerical matrices and complete scalar reconstruction; closed form for all L,N established by exact recurrence checks.'),
    12: ('b5-02 through b5-15', 'Separate native symbolic step, base, first/last step, N=1 and boundary checks; every Gram/function/offset residual exactly zero; signs/domain/normalization justified.')}
for i, line in enumerate(lines):
    if line.startswith('Last reviewed block:'):
        lines[i] = 'Last reviewed block: B5 (complete)'
    elif line.startswith('SHA-256:'):
        lines[i] = 'SHA-256: ' + checksum
    elif line.startswith('| ') and '. ' in line:
        number = int(line.split('|')[1].strip().split('.')[0])
        item = line.split('|')[1].strip()
        cells, evidence = updates[number]
        lines[i] = f'| {item} | verified | {cells} | {evidence} |'
lines.append('\nFinal execution: supplementary/b5-nbconvert-001-output.txt. Static: supplementary/b5-static-001.json. Presentation override: no rendered/image inspection, exports, or browser use. Final post-execution edits changed only historical Markdown status wording; code hash unchanged.')
checkpath.write_text('\n'.join(lines), encoding='utf-8')
state = json.loads((root / 'state/dual_feg_b5.json').read_text())
assert state['lyapunov_proof_verified'] and all(state['proof_checks'].values())
evidence = {'notebook_sha256': checksum, 'executed_code_sha256': code_after,
            'code_unchanged_by_final_markdown_edits': True, 'code_cells': sum(c.cell_type=='code' for c in nb.cells),
            'cell_count': len(nb.cells), 'all_executed_without_error': True,
            'twelve_items_verified': True, 'presentation_policy': 'evaluation-ancillary-v1',
            'rendered_visual_inspection': False, 'notebook': path.name,
            'static_evidence': 'supplementary/b5-static-001.json',
            'execution_evidence': 'supplementary/b5-nbconvert-001-output.txt'}
(root / 'supplementary/b5-final-audit.json').write_text(json.dumps(evidence, indent=2))
print(json.dumps(evidence, indent=2))
print('Final formula:', state['lyapunov_formula'])
print('Theorem LaTeX:', state['theorem_latex'])
