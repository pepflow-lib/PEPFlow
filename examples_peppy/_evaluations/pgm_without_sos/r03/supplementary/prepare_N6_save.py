from pathlib import Path
root=Path.cwd()
s=(root/'supplementary/save_b2.py').read_text(encoding='utf-8-sig')
s=s[:s.index('book=nbformat.read')]
s=s.replace("cells=(root/'supplementary/b2_cells.py').read_text(encoding='utf-8-sig')", "cells=(root/'supplementary/b2_cells.py').read_text(encoding='utf-8-sig').replace('state/pgm_dense.json','supplementary/pgm_dense_N6.json').replace('supplementary/sparse-trial.json','supplementary/sparse-trial-N6.json')")
s=s.replace("for filename in ('pgm_b2.json','pgm_relaxed.json'):","for filename in ('pgm_b2_N6.json',):").replace("(root/'state'/filename)","(root/'supplementary'/filename)")
s+='\nprint("Additional N6 coherent sample saved.")\n'
(root/'supplementary/save_b2_N6.py').write_text(s)
