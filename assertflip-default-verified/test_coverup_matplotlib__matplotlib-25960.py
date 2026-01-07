import pytest
import matplotlib.pyplot as plt

def test_subfigures_wspace_hspace_bug():
    # Create a figure with subfigures using specific wspace and hspace
    fig = plt.figure()
    subfigs = fig.subfigures(2, 2, wspace=0.5, hspace=0.5)
    
    # Iterate over subfigures and add a simple plot to each
    for subfig in subfigs.flat:
        ax = subfig.subplots()
        ax.plot([1, 2])
    
    # Check the layout properties to confirm the bug
    # We expect the wspace and hspace to affect the layout
    for subfig in subfigs.flat:
        # Assert that the wspace and hspace are as expected
        assert subfig.subplotpars.wspace == 0.5  # This should be 0.5
        assert subfig.subplotpars.hspace == 0.5  # This should be 0.5

    # Cleanup: Close the figure to avoid state pollution
    plt.close(fig)
