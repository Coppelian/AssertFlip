import matplotlib.pyplot as plt
import numpy as np
import pytest

def test_contour_with_boolean_array():
    # Create a 2D boolean array
    boolean_2d_array = (np.indices((100, 100)).sum(axis=0) % 20) < 10
    
    # Create a contour plot with the boolean array without specifying levels
    contour_set = plt.contour(boolean_2d_array)
    
    # Extract the levels used in the contour plot
    levels = contour_set.levels
    
    # Assert that the levels are set to [0.5], which is the expected correct behavior
    assert np.array_equal(levels, [0.5]), "Levels should default to [0.5] for boolean arrays"
    
    # Cleanup: Close the plot to avoid state pollution
    plt.close()
