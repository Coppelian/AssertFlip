import pytest
import numpy as np
from sklearn.metrics.cluster import fowlkes_mallows_score

def test_fowlkes_mallows_score_overflow():
    # Create large label arrays to trigger overflow
    # These arrays are designed to create large pk and qk values
    labels_true = np.array([0] * 100000 + [1] * 100000)
    labels_pred = np.array([0] * 50000 + [1] * 50000 + [2] * 50000 + [3] * 50000)

    # Call the fowlkes_mallows_score function
    score = fowlkes_mallows_score(labels_true, labels_pred)

    # Assert that the score is not nan, indicating the bug is fixed
    assert not np.isnan(score), "BUG: Expected a valid score, but got nan due to overflow"

# Note: This test is expected to fail by confirming the presence of the bug.
# Once the bug is fixed, the test should pass, indicating the function now returns a valid float without warnings.

