from sympy import symbols, exp, sinh, Piecewise
from sympy.core.cache import clear_cache
from sympy.polys.polyerrors import PolynomialError
from sympy.testing.pytest import raises

def test_subs_polynomial_error_with_real_symbols():
    from sympy import exp, sinh, Piecewise, symbols

    # Clear cache to ensure the bug is triggered
    from sympy.core.cache import clear_cache
    clear_cache()

    # Define real symbols
    x, y, z = symbols('x y z', real=True)

    # Define the expression as described in the issue ticket
    expr = exp(sinh(Piecewise((x, y > x), (y, True)) / z))

    # Assert that no PolynomialError is raised when subs is called
    try:
        expr.subs({1: 1.0})
    except PolynomialError:
        assert False, "PolynomialError was raised unexpectedly"
