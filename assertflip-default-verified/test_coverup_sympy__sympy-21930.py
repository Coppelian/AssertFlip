from sympy import Symbol
from sympy.physics.secondquant import B, Bd, Commutator
from sympy import init_printing
from sympy.printing.latex import latex

def test_latex_rendering_issue():
    # Initialize Latex printing
    init_printing()

    # Create a symbol
    a = Symbol('0')

    # Construct the commutator expression
    expr = Commutator(Bd(a)**2, B(a))

    # Capture the Latex output using the latex function
    latex_output = latex(expr)

    # Assert that the correct format is present
    assert "{b^\\dagger_{0}}^{2}" in latex_output
