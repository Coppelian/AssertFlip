import pytest
from astropy.io import fits

def test_double_single_quote_handling():
    # Test for the bug where double single-quotes are incorrectly transformed
    for n in range(60, 70):
        card1 = fits.Card('CONFIG', "x" * n + "''")
        card2 = fits.Card.fromstring(str(card1))
        
        # Assert that the values are equal, which is the expected correct behavior
        assert card1.value == card2.value
