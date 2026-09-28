from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'supplementary/b2_core.py'
s=p.read_text(encoding='utf-8-sig')
s=s.replace("        duals[c.name] = None if dropped else float(d)","        if dropped:\n            duals[c.name] = None\n        else:\n            assert d is not None\n            duals[c.name] = float(d)")
start=s.index('    source_paths =')
end=s.index('    data = dict',start)
hashes=s[start:end]
s=s[:start]+s[end:]
s=s.replace('    ctx, pb, obj = get_pep_setup(N, params)',hashes+'    ctx, pb, obj = get_pep_setup(N, params)')
p.write_text(s)
p=root/'supplementary/update_b2_notebook.py'
s=p.read_text(encoding='utf-8-sig').replace('code(core),', 'code(core[core.index("import hashlib"):].replace("from bppm_setup import get_pep_setup\\n", "")),')
s=s.replace('nb.cells[10:12]=new', 'end = next(i for i,c in enumerate(nb.cells) if c.cell_type == "markdown" and c.source.startswith("## Lyapunov partial sums"))\nnb.cells[10:end]=new')
p.write_text(s)
p=root/'supplementary/run_b2_selected.py'
s=p.read_text(encoding='utf-8-sig')
s=s.replace('state={**b1,**data}', '''lambda_data = result.get_scalar_constraint_dual_value_in_numpy(obj=next(owner for owner in ctx.func_to_triplets if str(owner)=='f'))
state={**b1,**data}''') if False else s
s=s.replace('state={**b1,**data}', '''lambda_data = result.get_scalar_constraint_dual_value_in_numpy(next(owner for owner in ctx.func_to_triplets if str(owner)=='f'))
def display(value):
    return dict(matrix=value.matrix.tolist(),row_names=list(value.row_names),col_names=list(value.col_names))
if isinstance(lambda_data,dict):
    data['lambda_groups']={name:display(value) for name,value in lambda_data.items()}
else:
    data.update(lambda_matrix=lambda_data.matrix.tolist(),lambda_row_names=list(lambda_data.row_names),lambda_col_names=list(lambda_data.col_names))
state={**b1,**data}''')
p.write_text(s)
