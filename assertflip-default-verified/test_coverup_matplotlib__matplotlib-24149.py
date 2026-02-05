import pytest
import numpy as np
import matplotlib.pyplot as plt

def test_bar_with_nan_values_does_not_raise():
    # Set up a plot
    fig, ax = plt.subplots()

    # Test input with NaN values
    x = [np.nan]
    height = [np.nan]

    # Ensure no exception is raised
    try:
        ax.bar(x, height)
    except StopIteration:
        pytest.fail("StopIteration was raised")

    # Cleanup
    plt.close(fig)
