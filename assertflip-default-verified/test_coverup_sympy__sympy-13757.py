from sympy import symbols, Poly

x = symbols('x')

def test_multiply_expression_by_poly():
    # Multiplying a symbolic expression by a Poly with the expression on the left
    result = x * Poly(x)
    # Correct behavior should be a Poly object representing x**2
    assert str(result) == "Poly(x**2, x, domain='ZZ')"
