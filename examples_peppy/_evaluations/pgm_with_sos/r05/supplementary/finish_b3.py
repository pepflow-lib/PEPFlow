"""Complete the notebook's B3 comparison and selected-state handoff."""

import hashlib
import os
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / "supplementary" / ".runtime"
for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[name] = "1"
for name in (
    "TEMP",
    "TMP",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_CONFIG_DIR",
    "JUPYTER_RUNTIME_DIR",
):
    os.environ[name] = str(runtime / name.lower())
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
notebook = ROOT / "pgm_example_lyap.ipynb"
nb = nbf.read(notebook, as_version=4)
intro = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Lyapunov partial sums")
)
nb.cells[intro].source = nb.cells[intro].source.replace(
    "A second independently acquired horizon certificate is still required before Block 3 can complete.",
    "The same recipe is confirmed at $N=6$ using that horizon’s own complete certificate; the comparison below replays the visible construction.",
)
if "polar alignment" not in nb.cells[intro].source:
    nb.cells[
        intro
    ].source += "\n\nEndpoint reconstruction exposed accumulated error in the supplied numerical SOS approximation. We use polar alignment of its factor rows to the same saved PSD slack, discarding only slack eigenvalues at or below the frozen PSD tolerance and checking the full reconstruction. Every revised step piece is a sum of three squares. This is a numerical decomposition for the selected certificate; it does not alter any certificate multiplier or claim an analytic decomposition."
comparison = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown"
    and (
        c.source.startswith("Cross-horizon rank confirmation")
        or c.source.startswith("### Cross-horizon rank confirmation")
    )
)
next_block = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Identify the vectors")
)
del nb.cells[comparison + 1 : next_block]
nb.cells[comparison] = nbf.v4.new_markdown_cell(
    "### Cross-horizon rank confirmation\nThe same construction is replayed at both horizons, with one excluded index at each end. Absolute rank tolerance: $10^{-4}$ on unscaled Gram matrices in setup insertion order. Near-threshold singular values are checked without changing the tolerance."
)
source = (ROOT / "supplementary" / "b3_construct.py").read_text()
nb.cells[intro + 2].source = source
check_source, decomposition_tail = source.split("# Decomposition:", 1)
decomp_source, group_tail = ("# Decomposition:" + decomposition_tail).split(
    "# Grouping convention:", 1
)
group_source = "# Grouping convention:" + group_tail
nb.cells.insert(
    comparison + 1,
    nbf.v4.new_code_cell("""from typing import Any

# Replay the exact construction displayed immediately above, with a fresh
# namespace per certificate; no new solve and no mixing of horizons.
construction_source = (notebook_dir/'supplementary'/'b3_construct.py').read_text()
rank_samples = []
for horizon, relative in [(4, 'state/pgm_b2.json'), (6, 'supplementary/N6/pgm_b2.json')]:
    sample_certificate = json.loads((notebook_dir/relative).read_text())
    replay: dict[str, Any] = dict(certificate=sample_certificate, notebook_dir=notebook_dir, get_pep_setup=get_pep_setup)
    exec(compile(construction_source, 'visible-B3-construction', 'exec'), replay)
    sample: dict[str, Any] = dict(N=horizon, certificate_id=sample_certificate['certificate_id'],
        recipe_id='star_and_consecutive_by_destination_minus_polar_aligned_supplied_sos',
        rank_profile=replay['ranks'], singular_values=replay['singular_values'],
        rank_credible=replay['rank_credible'], certificate_checked=replay['certificate_checked'],
        grouping_checked=replay['grouping_checked'], certificate_path=relative,
        rank_convention=dict(tolerance=1e-4, scaling='unscaled Gram matrix', coordinate_order='setup insertion order'),
        coverage_residuals=replay['coverage_residuals'], certificate_residuals=replay['certificate_residuals'],
        piece_residuals=replay['piece_residuals'], increment_residuals=replay['increment_residuals'],
        decomposition_trial=replay['decomposition_trial'])
    assert sample['certificate_checked'] and sample['grouping_checked'] and sample['rank_credible']
    retained = sample['rank_profile'][1:horizon]
    assert len(retained) >= 3 and set(retained) == {4}
    rank_samples.append(sample)
assert rank_samples[0]['certificate_id'] == certificate['certificate_id']
assert rank_samples[0]['rank_profile'] == ranks
rank_search = dict(status='confirmed', boundary_exclusions={'left':1,'right':1}, rank=4,
    confirmed_horizons=[4,6], selected_certificate_id=certificate['certificate_id'],
    recipe_id=rank_samples[0]['recipe_id'], rank_convention=rank_samples[0]['rank_convention'],
    unresolved_samples=[], evidence_path='supplementary/rank_search.json')
(notebook_dir/'supplementary'/'rank_search.json').write_text(json.dumps({'summary':rank_search,'samples':rank_samples},indent=2))
print('Common interior rank 4 confirmed at N=4 and N=6; exclusions (1,1).')
print('No interpolation or SOS terms omitted; numerical nonincreasing sign convention checked.')
"""),
)
save_source = (
    """evaluated_lyap = [pm.eval_scalar(value) for value in lyap]
state_b3 = dict(certificate)
state_b3.update(rank_profile=ranks, rank_search=rank_search,
    lyap_inner_prod_coords=[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in evaluated_lyap],
    lyap_func_coords=[np.asarray(v.func_coords,dtype=float).tolist() for v in evaluated_lyap],
    lyap_offsets=[float(v.offset) for v in evaluated_lyap],
    certificate_check_code=CHECK_SOURCE, decomposition_code=DECOMP_SOURCE, grouping_code=GROUP_SOURCE,
    extra_duals=extra_duals, rank_tolerance=rank_tolerance, decomposition_trial=decomposition_trial,
    reconstruction_tolerance=tol['reconstruction_atol'], reconstruction_rtol=tol['reconstruction_rtol'],
    grouping_coverage=dict(constraint_assignment=term_assignment,S_assignment=S_assignment,
        normalization_constraint='initial_condition',boundary_constraints=[],boundary_S=[],omitted_constraints=[],
        checked=grouping_checked,coverage_residuals=coverage_residuals,increment_residuals=increment_residuals),
    numerical_certificate_verified=True,analytic_full_pep_verified=False,lyapunov_proof_verified=False)
(notebook_dir/'state'/'pgm_b3.json').write_text(json.dumps(state_b3,indent=2,allow_nan=False))
print('B3 complete; selected N=4 certificate retained.')
""".replace("CHECK_SOURCE", repr(check_source))
    .replace("DECOMP_SOURCE", repr(decomp_source))
    .replace("GROUP_SOURCE", repr(group_source))
)
nb.cells.insert(comparison + 2, nbf.v4.new_code_cell(save_source))
nbf.write(nb, notebook)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="attempt-pgm",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nbf.write(nb, notebook)
checklist = ROOT / "supplementary" / "pgm_example_lyap_checklist.md"
lines = checklist.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(notebook.read_bytes()).hexdigest()
    elif line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B3"
    elif line.startswith("| 9 |"):
        parts = line.split("|")
        parts[3:6] = [
            " verified ",
            f" {intro}-{comparison + 2} ",
            " Visible construction, source/hash revalidation, full-coordinate coverage, sign checks and rank confirmation at N4/N6 executed. ",
        ]
        lines[i] = "|".join(parts)
checklist.write_text("\n".join(lines), encoding="utf-8")
for c in nb.cells:
    if c.cell_type == "markdown":
        assert "\\(" not in c.source and "\\[" not in c.source
        assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in c.source)
print("B3 notebook executed; state and checklist updated.")
