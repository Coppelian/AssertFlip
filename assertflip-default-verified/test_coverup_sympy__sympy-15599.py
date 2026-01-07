from sympy import Symbol, Mod

def test_mod_simplification_bug():
    # Define a symbolic integer variable
    i = Symbol('i', integer=True)
    
    # Construct the expression Mod(3*i, 2)
    expr = Mod(3*i, 2)
    
    # Assert that the expression simplifies correctly
    assert expr == Mod(i, 2)
