from pathlib import Path
import nbformat
p=Path('feg_example_lyap.ipynb')
nb=nbformat.read(p,as_version=4)
for cell in nb.cells:
    if cell.cell_type!='code':continue
    if cell.source.startswith('import hashlib\nfrom pepflow.utils import Comparator'):
        cell.source += '\nfor group_name, matrix_data in dense["lambda_groups"].items():\n    print("Dense group:",group_name)\n    pf.pprint_labeled_matrix(pf.MatrixWithNames(np.array(matrix_data["matrix"]),matrix_data["row_names"],matrix_data["col_names"]))\nfor group_name, matrix_data in b2["lambda_groups"].items():\n    print("Selected relaxed group:",group_name)\n    pf.pprint_labeled_matrix(pf.MatrixWithNames(np.array(matrix_data["matrix"]),matrix_data["row_names"],matrix_data["col_names"]))'
    if cell.source.startswith('basis = ctx.basis_vectors()'):
        cell.source=cell.source.replace('pf.pprint_labeled_matrix(pf.MatrixWithNames(S_guess_matrix,b2["basis_vectors"],b2["basis_vectors"]))\n','')
nbformat.write(nb,p)
