import pytest
import numpy as np
import xarray as xr

def test_weighted_mean_with_boolean_weights():
    # Setup: Create a DataArray with sample data
    data = xr.DataArray([1.0, 1.0, 1.0])
    
    # Setup: Create a DataArray for weights using boolean values
    weights = xr.DataArray(np.array([True, True, False], dtype=bool))
    
    # Apply the weighted.mean() function
    result = data.weighted(weights).mean()
    
    # Assert the correct behavior
    assert result.item() == 1.0  # The expected correct behavior
