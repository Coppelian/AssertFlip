from sympy import symbols
from sympy.printing.latex import latex

def test_latex_custom_mul_symbol():
    x, y = symbols('x y')
    expr = 3 * x**2 * y
    # Attempt to use a custom mul_symbol that is not in the predefined list
    result = latex(expr, mul_symbol="\\,")
    assert result == '3 \\, x^{2} \\, y'
