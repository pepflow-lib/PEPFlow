from pathlib import Path
root=Path.cwd()
source=(root/'supplementary/b2_finalize.py').read_text(encoding='utf-8-sig')
source=source.replace("N=b1['N_verify']","N=6")
source=source.replace("dense=json.loads((ROOT/'state/feg_dense.json').read_text())\ndrops=json.loads((ROOT/'state/feg_relaxed_constraints.json').read_text())",'''_,_,_,_,_,dense=capture(N,[])
(ROOT/'supplementary/b2-N6-dense.json').write_text(json.dumps(dense,indent=2))
prior=json.loads((ROOT/'state/feg_b2.json').read_text())
exec(prior['lamb_code'])
drops=[name for name in dense['named_dual_values'] if name!='initial_condition' and lambda_candidate(name,N,params['L'])==0]
(ROOT/'supplementary/b2-N6-relaxed-constraints.json').write_text(json.dumps(drops,indent=2))''')
source=source.replace("for name in ('feg_b2.json','feg_relaxed.json'):\n    (ROOT/'state'/name)","for name in ('b2-N6.json',):\n    (ROOT/'supplementary'/name)")
(root/'supplementary/b2_N6.py').write_text(source,encoding='utf-8')
