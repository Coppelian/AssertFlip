import pytest
from unittest.mock import patch
from sklearn.utils._show_versions import _get_deps_info

def test_joblib_presence_in_deps_info():
    # Mock the sklearn version to be greater than 0.20
    with patch('sklearn.__version__', '0.22.dev0'):
        # Call the function to get dependencies info
        deps_info = _get_deps_info()
        
        # Assert that 'joblib' is present in the dependencies info
        assert 'joblib' in deps_info
