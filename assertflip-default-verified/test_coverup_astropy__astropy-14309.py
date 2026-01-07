import pytest
from astropy.io.registry import identify_format
from astropy.table import Table

def test_identify_format_with_empty_args():
    # Prepare a non-FITS file path and empty args
    non_fits_filepath = "bububu.ecsv"
    empty_args = []

    # Call identify_format with parameters that lead to is_fits being called with empty args
    result = identify_format("write", Table, non_fits_filepath, None, empty_args, {})
    
    # Assert that the function handles empty args gracefully and does not raise IndexError
    assert result is not None
