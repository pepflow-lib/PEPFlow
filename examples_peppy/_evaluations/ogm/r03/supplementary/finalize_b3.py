"""Confirm rank and coverage across two saved coherent certificates."""
import inspect
import json
import os
from pathlib import Path
import sys
import textwrap

ROOT=Path(__file__).resolve().parents[1]
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[key]="1"
sys.path[:0]=[str(ROOT/"supplementary"/"approved"),str(ROOT),str(ROOT/"supplementary"/"helpers")]
import nbformat as nbf  # noqa: E402
from partial_sums import build_partial_sums, check_certificate  # noqa: E402

selected=json.loads((ROOT/"state"/"ogm_b2.json").read_text())
other=json.loads((ROOT/"supplementary"/"b2-N6-certificate.json").read_text())
observations=[]
selected_coordinates=selected_coverage=None
for certificate in (selected,other):
    observation,coordinates,coverage=build_partial_sums(certificate,ROOT)
    observations.append(observation)
    if certificate is selected:
        selected_coordinates,selected_coverage=coordinates,coverage
    (ROOT/"supplementary"/f'b3-N{certificate["N"]}-observation.json').write_text(json.dumps(dict(observation=observation,coordinates=coordinates,coverage=coverage),indent=2))
assert selected_coordinates is not None and selected_coverage is not None
for observation in observations:
    assert observation["rank_credible"] and observation["certificate_checked"] and observation["grouping_checked"]
    retained=observation["rank_profile"][2:observation["N"]+1]
    assert len(retained)>=3 and set(retained)=={4}
    assert observation["recipe_id"]==observations[0]["recipe_id"]
    assert observation["rank_convention"]==observations[0]["rank_convention"]
rank_search=dict(status="confirmed",boundary_exclusions={"left":2,"right":0},rank=4,confirmed_horizons=[4,6],selected_certificate_id=selected["certificate_id"],recipe_id=observations[0]["recipe_id"],rank_convention=observations[0]["rank_convention"],unresolved_samples=[],evidence_path="supplementary/rank_search.json")
(ROOT/"supplementary"/"rank_search.json").write_text(json.dumps(dict(summary=rank_search,samples=observations),indent=2))
helper=(ROOT/"supplementary"/"helpers"/"partial_sums.py").read_text()
grouping_source=inspect.getsource(build_partial_sums)
decomposition_source=textwrap.dedent(grouping_source.split('    basis = ctx.basis_vectors()',1)[1].split('    group_terms =',1)[0])
decomposition_source='basis = ctx.basis_vectors()\n'+decomposition_source
state={**selected,**selected_coordinates,"rank_profile":observations[0]["rank_profile"],"rank_search":rank_search,"certificate_check_code":helper.split('def build_partial_sums',1)[0]+'\nctx, pb, obj, pm, weighted_terms, residuals = check_certificate(certificate, notebook_dir)\n',"decomposition_code":decomposition_source,"grouping_code":grouping_source+'\nobservation, coordinates, grouping_coverage = build_partial_sums(certificate, notebook_dir)\n',"extra_duals":{},"rank_tolerance":1e-4,"reconstruction_tolerance":1e-4,"reconstruction_rtol":1e-5,"grouping_coverage":selected_coverage}
(ROOT/"state"/"ogm_b3.json").write_text(json.dumps(state,indent=2))
path=ROOT/"ogm_example_lyap.ipynb"
nb=nbf.read(path,as_version=4)
nb.cells=nb.cells[:-1]
nb.cells.extend([
nbf.v4.new_markdown_cell(r"""## Lyapunov partial sums and rank comparison
Normalize each smooth-convex interpolation inequality as $I_{i,j}\leq0$. Starting from $V_0=0$, group
$$V_{k+1}-V_k=\lambda_{\star,k}I_{\star,k}+\lambda_{k,k+1}I_{k,k+1}\leq0.$$
The terminal inequality $\lambda_{\star,N}I_{\star,N}$ and the complete PSD matrix $S$ remain as the single interpolation and PSD boundary terms. Thus every interpolation contribution is accounted for, and no small numerical term is discarded. The initial-condition contribution is reserved for the boundary argument.

Both horizons 4 and 6 have rank 4 after excluding $V_0,V_1$ and excluding no terminal index. At horizon 4 this retains three indices. Ranks use absolute tolerance $10^{-4}$ without rescaling. Rank agreement is numerical discovery evidence; it is not a universal proof.
"""),
nbf.v4.new_code_cell(inspect.getsource(check_certificate)),
nbf.v4.new_code_cell(grouping_source+'\nselected_certificate = json.loads((notebook_dir / "state" / "ogm_b2.json").read_text())\nselected_observation, selected_coordinates, selected_coverage = build_partial_sums(selected_certificate, notebook_dir)\n'),
nbf.v4.new_code_cell('other_certificate = json.loads((notebook_dir / "supplementary" / "b2-N6-certificate.json").read_text())\nother_observation, other_coordinates, other_coverage = build_partial_sums(other_certificate, notebook_dir)\nfor observation in (selected_observation, other_observation):\n    retained = observation["rank_profile"][2:observation["N"]+1]\n    assert len(retained) >= 3 and set(retained) == {4}\n    assert observation["rank_credible"]\n    print("Horizon", observation["N"], "coverage residual", observation["coverage_max_abs"])\nprint("Confirmed common rank: 4; horizons: 4, 6; exclusions: (2,0); absolute tolerance: 1e-4")\nprint("Selected boundary contributions:", selected_coverage["boundary_constraints"], selected_coverage["boundary_S"])'),
nbf.v4.new_markdown_cell("## Identify the vectors composing the Lyapunov function (pending Block 4)\n## Closed-form Lyapunov function and symbolic identities (pending Block 5)")])
nbf.write(nb,path)
checklist=ROOT/"supplementary"/"ogm_example_lyap_checklist.md"
lines=checklist.read_text().replace("Last reviewed block: B2","Last reviewed block: B3").splitlines()
for i,line in enumerate(lines):
    if line.startswith("| 9 |"):
        fields=line.split("|")
        fields[3]=" verified "
        fields[4]=" 17-20 "
        fields[5]=" Recomputed full-coordinate coverage and rank comparison at N=4,6, fixed exclusions (2,0). "
        lines[i]="|".join(fields)
checklist.write_text("\n".join(lines))
print(json.dumps(rank_search))
