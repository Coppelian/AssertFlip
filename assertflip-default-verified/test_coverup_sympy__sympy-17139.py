from sympy import Symbol, cos, I
from sympy.simplify import simplify

def test_simplify_cos_complex_exponent():
    x = Symbol('x')
    expr = cos(x)**I
    try:
        result = simplify(expr)
    except TypeError:
        assert False, "TypeError was raised"
    else:
        assert result is not None, "Simplification did not return a result"

