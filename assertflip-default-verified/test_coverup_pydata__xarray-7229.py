import xarray as xr
import pytest

def test_xr_where_overwrites_coordinate_attrs():
    # Load the sample dataset
    ds = xr.tutorial.load_dataset("air_temperature")
    
    # Perform the xr.where operation with keep_attrs=True
    result = xr.where(True, ds.air, ds.air, keep_attrs=True)
    
    # Retrieve the attributes of the 'time' coordinate
    result_time_attrs = result['time'].attrs
    
    # Assert that the attrs are correct (i.e., they should not match the variable attributes)
    assert result_time_attrs == {'standard_name': 'time', 'long_name': 'Time'}
