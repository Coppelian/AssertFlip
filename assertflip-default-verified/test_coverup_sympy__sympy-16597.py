from sympy import Symbol

def test_even_symbol_is_finite():
    # Create a symbol with the assumption that it is even
    m = Symbol('m', even=True)
    
    # Check the is_finite property
    is_finite_result = m.is_finite
    
    # Assert that is_finite should be True, as an even number should be finite
    assert is_finite_result is True
