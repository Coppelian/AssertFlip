import matplotlib.pyplot as plt
import pytest

def test_offset_text_color_bug():
    # Set the labelcolor to a distinct color
    plt.rcParams.update({'ytick.labelcolor': 'red', 'ytick.color': 'blue'})
    
    # Create a figure and axis with large numbers to ensure offsetText is displayed
    fig, ax = plt.subplots()
    ax.plot([1.01e9, 1.02e9, 1.03e9])
    
    # Draw the canvas to ensure all elements are rendered
    fig.canvas.draw()
    
    # Get the offset text color
    offset_text_color = ax.yaxis.offsetText.get_color()
    
    # Assert that the offset text color is correctly set to ytick.labelcolor
    assert offset_text_color == 'red', "BUG: offsetText color should be set to ytick.labelcolor"

    # Cleanup
    plt.close(fig)

