import numpy as np

from pepflow import ipython_utils


def test_pprint_labeled_matrix_handles_empty_matrix(monkeypatch):
    displayed = []
    monkeypatch.setattr(ipython_utils, "display", displayed.append)

    raw_matrix = np.zeros((0, 0))

    returned = ipython_utils.pprint_labeled_matrix(
        raw_matrix, [], [], return_matrix=True
    )

    assert returned is raw_matrix
    assert len(displayed) == 1
    assert "Empty matrix" in displayed[0].data
