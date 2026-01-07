from sympy import exp
from sympy.physics import units
from sympy.physics.units.systems.si import SI

def test_dimensionless_exponent_bug():
    # Setup the expression
    expr = units.second / (units.ohm * units.farad)
    buggy_expr = 100 + exp(expr)
    
    # Assert the correct behavior: no exception should be raised
    try:
        SI._collect_factor_and_dimension(buggy_expr)
    except ValueError:
        assert False, "ValueError raised, but the expression should be dimensionless."
