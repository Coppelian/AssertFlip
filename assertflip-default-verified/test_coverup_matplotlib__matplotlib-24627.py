import matplotlib.pyplot as plt
import pytest

def test_cla_unsets_axes_attribute():
    # Create a figure and axes
    fig, ax = plt.subplots()
    
    # Plot a line to create an artist
    line, = ax.plot([1, 2])
    
    # Clear the axes using cla()
    ax.cla()
    
    # Assert that the .axes attribute of the artist is None
    assert line.axes is None

    # Cleanup
    plt.close(fig)

