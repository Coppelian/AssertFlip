import numpy as np
import xarray as xr
import pytest

def test_coarsen_construct_preserves_coordinates():
    # Setup: Create a DataArray with a non-dimensional coordinate
    da = xr.DataArray(np.arange(24), dims=["time"])
    da = da.assign_coords(day=365 * da)
    ds = da.to_dataset(name="T")

    # Apply coarsen.construct
    result = ds.coarsen(time=12).construct(time=("year", "month"))

    # Assert that 'day' remains a coordinate
    assert 'day' in result.coords

    # Assert that 'day' is not demoted to a variable
    assert 'day' not in result.variables
