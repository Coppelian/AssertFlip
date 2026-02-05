import pytest
import xarray as xr
import numpy as np

def test_combine_by_coords_non_monotonic_identical_coords():
    # Setup datasets with non-monotonic identical coordinates
    yCoord = ['a', 'c', 'b']  # Non-monotonic order
    ds1 = xr.Dataset(
        data_vars=dict(
            data=(['x', 'y'], np.random.rand(3, 3))
        ),
        coords=dict(
            x=[1, 2, 3],
            y=yCoord
        )
    )
    ds2 = xr.Dataset(
        data_vars=dict(
            data=(['x', 'y'], np.random.rand(4, 3))
        ),
        coords=dict(
            x=[4, 5, 6, 7],
            y=yCoord
        )
    )

    # Attempt to combine datasets and expect no error
    try:
        xr.combine_by_coords((ds1, ds2))
    except ValueError as e:
        pytest.fail(f"combine_by_coords raised ValueError unexpectedly: {e}")

