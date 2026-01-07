from sympy import Subs, latex
from sympy.abc import x, y

def test_incorrect_parenthesizing_of_subs():
    # Create a Subs object with the expression -x + y, substituting x with 1
    subs_expr = Subs(-x + y, (x,), (1,))
    
    # Multiply the Subs object by 3
    expr = 3 * subs_expr
    
    # Convert the expression to a LaTeX string
    latex_str = latex(expr)
    
    # Assert that the LaTeX string matches the correct format
    assert latex_str == r'3 \left. \left(- x + y\right) \right|_{\substack{ x=1 }}'
