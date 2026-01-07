import pytest
from astropy.io.ascii.qdp import _line_type

def test_line_type_lowercase_command():
    # Test with a lowercase command that should be recognized
    line = "read serr 1 2"
    
    # The test should pass if the line is correctly recognized and does not raise an error
    assert _line_type(line) is not None
