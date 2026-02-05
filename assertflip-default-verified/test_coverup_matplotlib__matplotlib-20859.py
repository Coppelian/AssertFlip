import pytest
import matplotlib.pyplot as plt

def test_legend_on_subfigure_creates_legend():
    # Create a SubFigure
    fig = plt.figure()
    subfig = fig.subfigures()
    ax = subfig.subplots()

    # Plot some data with a label
    ax.plot([0, 1, 2], [0, 1, 2], label="test")

    # Attempt to add a legend to the SubFigure and assert that it does not raise an error
    try:
        subfig.legend()
    except TypeError:
        pytest.fail("Legend should be created without raising TypeError")
