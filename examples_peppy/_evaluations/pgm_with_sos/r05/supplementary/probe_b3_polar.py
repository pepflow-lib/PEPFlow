from pathlib import Path
import json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
for n,p in [(4,ROOT/'state'/'pgm_b2.json'),(6,ROOT/'supplementary'/'N6'/'pgm_b2.json')]:
 c=json.loads(p.read_text()); S=np.array(c['S_matrix']); D=np.array(c['numerical_decomposition']['D']); E=np.array(c['numerical_decomposition']['ell_coords']); A=np.sqrt(D)@E
 print(n,'candidate eig',np.linalg.eigvalsh(A.T@A),'actual eig',np.linalg.eigvalsh(S))
 U,s,Vt=np.linalg.svd(A,full_matrices=False)
 eig,V=np.linalg.eigh(S)
 # Noise below frozen dual/PSD tolerance is retained in certificate but dropped
 # from trial decomposition only subject to full reconstruction checks.
 root=V@np.diag(np.sqrt(np.where(eig>1e-6,eig,0)))@V.T
 Acorrect=U@Vt@root
 pieces=[Acorrect[3*i:3*i+3].T@Acorrect[3*i:3*i+3] for i in range(n)]
 out=dict(pieces=[x.tolist() for x in pieces],correction_factor=Acorrect.tolist(),reconstruction_max_abs=float(np.max(np.abs(sum(pieces)-S))),reconstruction_fro=float(np.linalg.norm(sum(pieces)-S)),method='polar alignment to PSD slack with eigenvalues <=1e-6 omitted and reconstruction checked')
 (ROOT/'supplementary'/f'b3-polar-N{n}.json').write_text(json.dumps(out,indent=2))
 print('residual',out['reconstruction_fro'],'piece deviations',[np.linalg.norm(x-y) for x,y in zip(pieces,np.array(c['numerical_decomposition']['pieces']))])
