import pytest
import numpy as np
from sklearn.linear_model import RidgeClassifierCV

def test_ridge_classifier_cv_store_cv_values():
    # Create a small random dataset
    X = np.random.randn(10, 5)
    y = np.random.randint(0, 2, size=10)

    # Attempt to initialize RidgeClassifierCV with store_cv_values=True
    try:
        model = RidgeClassifierCV(alphas=np.arange(0.1, 10, 0.1), normalize=True, store_cv_values=True)
        model.fit(X, y)
        # If no error is raised, check if cv_values_ attribute exists
        assert hasattr(model, 'cv_values_')
    except TypeError as e:
        # Fail the test if TypeError is raised
        pytest.fail(f"TypeError raised: {e}")
