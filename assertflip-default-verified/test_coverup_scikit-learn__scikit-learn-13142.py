import pytest
import numpy as np
from sklearn.mixture import GaussianMixture

def test_gaussian_mixture_fit_predict_discrepancy():
    # Generate random data with a fixed seed for reproducibility
    rng = np.random.RandomState(42)
    X = rng.randn(1000, 5)

    # Initialize GaussianMixture with n_components=5 and n_init=5
    gm = GaussianMixture(n_components=5, n_init=5, random_state=42)

    # Fit and predict using fit_predict
    c1 = gm.fit_predict(X)

    # Predict using predict
    c2 = gm.predict(X)

    # Assert that the results are the same, which is the expected correct behavior
    assert np.array_equal(c1, c2), "fit_predict and predict should agree when n_init > 1"

# Note: This test will fail if the bug is present, as it asserts the correct behavior.
