import numpy as np
import matplotlib.pyplot as plt
import pytest

def test_invert_axis_log_scale():
    # Create a dataset with values suitable for both linear and log scales
    y = np.linspace(1000e2, 1, 100)
    x = np.exp(-np.linspace(0, 1, y.size))

    # Iterate over both linear and log scales
    for yscale in ('linear', 'log'):
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_yscale(yscale)
        ax.set_ylim(y.max(), y.min())  # Attempt to invert the y-axis

        # Capture the y-axis limits after setting them
        bottom, top = ax.get_ylim()

        # Assert that the y-axis limits are inverted for both linear and log scales
        assert bottom > top, f"{yscale.capitalize()} scale: y-axis should be inverted"

        plt.close(fig)  # Cleanup to avoid state pollution
