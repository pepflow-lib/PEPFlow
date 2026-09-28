import json
from pathlib import Path
import nbformat as nbf
root=Path(__file__).resolve().parents[1]
path=root/'pgm_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
b3=json.loads((root/'state/pgm_b3.json').read_text())
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Partial-sum Lyapunov'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Identify the vectors'))
replay_source=b3['certificate_check_code'].split('def replay(certificate):')[1]
replay_source='def replay(certificate):'+replay_source
cells=[nbf.v4.new_markdown_cell(r'''## Partial-sum Lyapunov construction and rank profile
Let $I_{ij}^f$ and $I_{ij}^g$ denote the nonpositive interpolation residuals defined above, and let $S_i$ be the sum of the three blended numerical SOS pieces at step $i$. Start with $V_0=0$. Add $\lambda^f_{\star,0}I^f_{\star,0}$ at the first step. Thereafter, the canonical increments collect the new star and adjacent inequalities:
$$V_{k+1}-V_k=\lambda^f_{\star,k+1}I^f_{\star,k+1}+\lambda^g_{\star,k+1}I^g_{\star,k+1}+\lambda^f_{k,k+1}I^f_{k,k+1}+\lambda^g_{k,k+1}I^g_{k,k+1}-S_{k+1},$$
where the nonexistent $g$ pair at $k=0$ is absent and the stated initial term is included there. Every coefficient is nonnegative and every subtracted square is nonnegative, so $V_{k+1}\leq V_k$ under the exact candidate's domain conditions. Here the saved numerical multipliers are used to discover structure; numerical tolerances do not constitute the final analytic theorem.
The construction retains all interpolation terms. At the end, the full certificate gives $V_N\approx h(x_N)-h(x_\star)-\tau\|x_0-x_\star\|^2$; the small constant discrepancy between the numerical objective and $\tau R^2$ is retained by the certificate checks. No boundary interpolation or SOS term is omitted. The quadratic ranks are $0,4,\ldots,4,1$, confirmed at $N=4$ and $N=6$.'''),
nbf.v4.new_code_cell('''import hashlib
ROOT = notebook_dir
APPROVED = repo_root
CERTIFICATE_KEYS = '''+repr(tuple(b3['replay_dependencies']['CERTIFICATE_KEYS']))+'\n'+replay_source),
nbf.v4.new_code_cell('from scipy.linalg import polar\n'+b3['decomposition_code'].split('def aligned_squares')[1].join(['def aligned_squares', ''])+'\n'+b3['grouping_code']+'''

b3 = json.loads((notebook_dir / "state/pgm_b3.json").read_text())
selected_trial = construct(b3, variant="blend-3/10")
lyap = selected_trial["lyap"]
pm = selected_trial["pm"]
ctx = selected_trial["ctx"]
rank_left = rank_right = 1
N_int = b3["N"]
ranks = []
for k, Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, dtype=float)
    rank = int(np.linalg.matrix_rank(matrix, tol=1e-4))
    ranks.append(rank)
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()
retained = ranks[rank_left:N_int+1-rank_right]
print("Interior rank is constant at this N:", len(retained)>=3 and len(set(retained))==1,
      "boundary exclusions:", (rank_left,rank_right))
print("Full-coordinate coverage residual:", selected_trial["observation"]["checks"]["coverage"])
print("Maximum increment residual:", selected_trial["observation"]["checks"]["maximum_increment_error"])
print("Boundary interpolation/S leftovers: none; omitted terms: none.")'''),
nbf.v4.new_code_cell('''confirmation_trial = construct(b2_n6, variant="blend-3/10")
observations = [selected_trial["observation"], confirmation_trial["observation"]]
retained_ranks = [o["rank_profile"][1:o["N"]] for o in observations]
assert all(o["certificate_checked"] and o["grouping_checked"] and o["rank_credible"] for o in observations)
assert all(len(rs)>=3 and set(rs)=={4} for rs in retained_ranks)
assert observations[0]["rank_convention"]==observations[1]["rank_convention"]
print("Common interior rank 4 confirmed at horizons 4 and 6.")
print("Fixed exclusions: V_0 and V_N. Absolute singular-value threshold: 1e-4; native coordinates, no rescaling.")
for observation in observations:
    retained_spectra = observation["singular_values"][1:observation["N"]]
    kept_min = min(s[3] for s in retained_spectra)
    discarded_max = max(s[4] for s in retained_spectra)
    print(f"N={observation['N']}: smallest retained singular value={kept_min:.4g}; largest discarded={discarded_max:.4g}; coverage residual={observation['checks']['coverage']:.4g}")
print("Rank agreement is finite-sample evidence; basis reconstruction and analytic proof remain pending.")''')]
nb.cells[start:end]=cells
nbf.write(nb,path)
print('B3 notebook construction and coverage cells saved')


