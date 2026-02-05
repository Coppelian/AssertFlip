from sympy import factor, expand, I
from sympy.abc import x, y

def test_factor_with_extension_bug():
    # Define the polynomial z
    z = expand((x - 1) * (y - 1))
    
    # Factor the polynomial with extension=[I]
    result = factor(z, extension=[I])
    
    # Assert that the result is equal to the expected correct factorization
    assert result == (x - 1) * (y - 1)
