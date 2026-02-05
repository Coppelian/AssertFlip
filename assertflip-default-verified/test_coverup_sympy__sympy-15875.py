from sympy import I, simplify

def test_is_zero_bug():
    # Define the complex expression
    e = -2*I + (1 + I)**2
    
    # Check the is_zero property
    result = e.is_zero
    
    # Assert that the result is None, which is the correct behavior
    assert result is None
