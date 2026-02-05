import pytest
import matplotlib.pyplot as plt
import pickle

def test_pickle_draggable_legend_state():
    # Create a figure and add a subplot
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Plot some data
    time = [0, 1, 2, 3, 4]
    speed = [40, 43, 45, 47, 48]
    ax.plot(time, speed, label="speed")

    # Add a draggable legend
    leg = ax.legend()
    leg.set_draggable(True)

    # Attempt to pickle the figure
    with pytest.raises(TypeError, match="cannot pickle 'FigureCanvasQTAgg' object"):
        pickle.dumps(fig)

    # Cleanup
    plt.close(fig)
