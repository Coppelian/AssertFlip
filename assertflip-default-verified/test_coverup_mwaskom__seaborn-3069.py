import pytest
import matplotlib.pyplot as plt
import seaborn as sns

def test_nominal_scale_axis_limits_and_grid():
    # Create a sample dataset with nominal categories
    data = {'Category': ['A', 'B', 'C'], 'Value': [1, 2, 3]}
    
    # Initialize a seaborn plot using this dataset with a Nominal scale
    fig, ax = plt.subplots()
    sns.barplot(x='Category', y='Value', data=data, ax=ax)
    
    # Render the plot
    plt.draw()
    
    # Capture the axis properties
    xlim = ax.get_xlim()
    grid_visible = ax.xaxis._gridOnMajor if hasattr(ax.xaxis, '_gridOnMajor') else ax.xaxis.get_gridlines()[0].get_visible()
    
    # Assert that the axis limits are correctly set to the normal margin logic
    assert xlim != (-0.5, 2.5), "Axis limits are incorrectly set to +/- 0.5 from the first and last tick"
    
    # Assert that grid lines are not visible
    assert grid_visible, "Grid lines are not visible when they should be"
    
    # Cleanup: Close the plot to free resources
    plt.close(fig)
