import pytest
import xarray as xr
import numpy as np

def test_stack_int32_to_int64_bug():
    # Create a dataset with a coordinate of dtype int32
    ds = xr.Dataset(coords={'a': np.array([0], dtype='i4')})
    
    # Perform the stack operation to create a MultiIndex
    stacked_ds = ds.stack(b=('a',))
    
    # Assert that the dtype of the original coordinate is int32
    assert ds['a'].values.dtype == np.int32
    
    # Assert that the dtype of the coordinate after stacking remains int32
    assert stacked_ds['a'].values.dtype == np.int32
