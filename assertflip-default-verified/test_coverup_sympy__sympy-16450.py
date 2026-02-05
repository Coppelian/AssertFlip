from sympy import Symbol, posify

def test_posify_finite_assumption():
    # Create a symbol with the finite=True assumption
    x = Symbol('x', finite=True)
    
    # Apply posify to the symbol
    xp, _ = posify(x)
    
    # Assert that the is_finite property is True, which is the expected correct behavior
    assert xp.is_finite is True
