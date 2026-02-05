import pytest
import xarray as xr

def test_merge_dataset_with_dataarray():
    # Create a Dataset and a DataArray
    ds = xr.Dataset({'a': 0})
    da = xr.DataArray(1, name='b')

    # Attempt to merge using ds.merge() and check if it matches the expected result
    expected = xr.merge([ds, da])
    actual = ds.merge(da)

    # Assert that the actual result matches the expected result
    xr.testing.assert_identical(expected, actual)
