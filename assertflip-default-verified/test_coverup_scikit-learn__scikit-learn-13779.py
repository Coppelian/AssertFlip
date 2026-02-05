import pytest
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.datasets import load_iris

def test_voting_classifier_with_none_estimator():
    # Load sample dataset
    X, y = load_iris(return_X_y=True)
    
    # Initialize VotingClassifier with two estimators
    voter = VotingClassifier(
        estimators=[('lr', LogisticRegression()), ('rf', RandomForestClassifier())]
    )
    
    # Fit the classifier with sample weights
    voter.fit(X, y, sample_weight=np.ones(y.shape))
    
    # Set one estimator to None
    voter.set_params(lr=None)
    
    # Attempt to fit the classifier again with sample weights
    # Check that no exception is raised, indicating the bug is fixed
    try:
        voter.fit(X, y, sample_weight=np.ones(y.shape))
    except AttributeError:
        pytest.fail("AttributeError raised when fitting with None estimator, bug not fixed.")
