import pytest
import numpy as np
from sklearn.linear_model import LogisticRegressionCV

def test_logistic_regression_cv_refit_false_index_error():
    # Set random seed for reproducibility
    np.random.seed(29)
    
    # Generate random data
    X = np.random.normal(size=(1000, 3))
    beta = np.random.normal(size=3)
    intercept = np.random.normal(size=None)
    y = np.sign(intercept + X @ beta)
    
    # Initialize LogisticRegressionCV with refit=False
    model = LogisticRegressionCV(cv=5, solver='saga', tol=1e-2, refit=False)
    
    # Expect no error to be raised when the bug is fixed
    try:
        model.fit(X, y)
    except IndexError:
        pytest.fail("IndexError was raised with refit=False, indicating a bug.")
