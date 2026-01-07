import pytest
import numpy as np
from sklearn.cluster import OPTICS

def test_optics_min_samples_float_bug():
    # Create a mock dataset
    data = np.random.rand(10, 2)  # 10 samples, 2 features

    # Instantiate OPTICS with min_samples as a float less than 1
    clust = OPTICS(min_samples=0.1)

    # Call fit to trigger the internal computation
    clust.fit(data)

    # Check if min_samples is correctly converted to an integer after internal computation
    assert isinstance(clust.min_samples, int), "min_samples should be an integer after computation"

