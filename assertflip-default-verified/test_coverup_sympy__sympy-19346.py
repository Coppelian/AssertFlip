from sympy import srepr
from sympy.abc import x, y

def test_srepr_set_and_dict():
    # Create a set and a dictionary with symbols
    symbol_set = {x, y}
    symbol_dict = {x: y}

    # Call srepr on the set and dictionary
    set_repr = srepr(symbol_set)
    dict_repr = srepr(symbol_dict)

    # Assert that the output is in the expected format
    assert set_repr == "{Symbol('x'), Symbol('y')}"
    assert dict_repr == "{Symbol('x'): Symbol('y')}"
