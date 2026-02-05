import pytest
import xarray as xr
from unittest.mock import patch

def test_chunksizes_triggers_data_load():
    # Setup: Open the dataset using the provided URL
    url = "https://ncsa.osn.xsede.org/Pangeo/pangeo-forge/swot_adac/FESOM/surf/fma.zarr"
    ds = xr.open_dataset(url, engine='zarr')

    # Mock the data loading function to track if it is called
    with patch('xarray.core.variable._as_array_or_item') as mock_as_array_or_item:
        # Access the chunksizes attribute
        chunksizes = ds.chunksizes

        # Assert that the mocked data loading function is not called, indicating the bug is fixed
        assert mock_as_array_or_item.call_count == 0  # Correct behavior: no data load should occur
