import pytest
import numpy as np
import matplotlib.pyplot as plt

def test_deprecation_warnings_with_empty_array():
    # Create an empty NumPy array with dtype=np.uint8
    empty_array = np.empty((0,), dtype=np.uint8)

    # Use pytest.warns to capture deprecation warnings
    with pytest.warns(DeprecationWarning) as record:
        plt.get_cmap()(empty_array)

    # Assert that no deprecation warnings are present
    assert len(record) == 0  # The test should pass when the bug is fixed and no warnings are present
