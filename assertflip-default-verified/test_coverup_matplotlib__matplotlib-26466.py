import matplotlib.pyplot as plt
import numpy as np
import pytest

def test_annotation_position_changes_with_array_modification():
    # Setup: Create a figure and axis
    fig, ax = plt.subplots()
    ax.set_xlim(-5, 5)
    ax.set_ylim(-3, 3)

    # Create an array and use it as the xy parameter in an annotation
    xy_0 = np.array([-4, 1])
    xy_f = np.array([-1, 1])
    annotation = ax.annotate('', xy=xy_0, xytext=xy_f, arrowprops=dict(arrowstyle='<->'))

    # Modify the array after the annotation is created
    xy_0[1] = 3

    # Check the position of the annotation to confirm it has not changed
    assert annotation.xy[1] == 1

    # Cleanup: Close the plot
    plt.close(fig)

