from sympy import Symbol, S, Eq, Limit
from sympy.printing.str import sstr

def test_sstr_eq_sympy_integers_bug():
    x = Symbol('x')
    y = S(1)/2
    result = sstr(Eq(x, y), sympy_integers=True)
    assert result == "Eq(x, S(1)/2)"

def test_sstr_limit_sympy_integers_bug():
    x = Symbol('x')
    result = sstr(Limit(x, x, S(1)/2), sympy_integers=True)
    assert result == "Limit(x, x, S(1)/2)"
