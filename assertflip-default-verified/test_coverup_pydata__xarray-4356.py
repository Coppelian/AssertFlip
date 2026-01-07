import pytest
import xarray as xr

def test_sum_with_min_count_multiple_dimensions():
    # Create a 2D DataArray
    da = xr.DataArray([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dims=["dim_0", "dim_1"])
    
    # Attempt to sum over multiple dimensions with min_count
    result = da.sum(dim=["dim_0", "dim_1"], min_count=1)
    
    # Check if the result is as expected when the bug is fixed
    expected_result = xr.DataArray(21.0)
    xr.testing.assert_identical(result, expected_result)
