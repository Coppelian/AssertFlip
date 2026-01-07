from sympy.utilities.lambdify import implemented_function
from sympy import Symbol

def test_evalf_composition_bug():
    # Define implemented functions
    f = implemented_function('f', lambda x: x ** 2)
    g = implemented_function('g', lambda x: 2 * x)
    
    # Create a symbol for evaluation
    x = Symbol('x')
    
    # Evaluate the composition f(g(2))
    result = f(g(2)).evalf()
    
    # Assert that the result is correctly evaluated
    assert result == 16.0
