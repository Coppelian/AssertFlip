import pytest
import xarray as xr

def test_merge_override_attrs_bug():
    # Create two datasets with distinct attributes
    xds1 = xr.Dataset(attrs={'a': 'b'})
    xds2 = xr.Dataset(attrs={'a': 'c'})

    # Merge datasets with combine_attrs='override'
    xds3 = xr.merge([xds1, xds2], combine_attrs='override')

    # Modify the attributes of the merged dataset
    xds3.attrs['a'] = 'd'

    # Assert that the original dataset's attributes have not changed
    assert xds1.attrs['a'] == 'b', "Original dataset's attribute should not change"

    # Cleanup: Reset the attribute to avoid side effects in other tests
    xds1.attrs['a'] = 'b'
