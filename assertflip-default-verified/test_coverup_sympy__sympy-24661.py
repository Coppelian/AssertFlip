from sympy.parsing.sympy_parser import parse_expr
from sympy import Lt

def test_parse_expr_evaluate_false_ignored_for_relationals():
    result = parse_expr('1 < 2', evaluate=False)
    assert result == Lt(1, 2, evaluate=False)
