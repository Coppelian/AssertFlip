from sympy.physics import units
from sympy.physics.units.systems.si import SI

def test_collect_factor_and_dimension_equivalent_dimensions():
    # Setup quantities with equivalent dimensions
    v1 = units.Quantity('v1')
    SI.set_quantity_dimension(v1, units.velocity)
    SI.set_quantity_scale_factor(v1, 2 * units.meter / units.second)

    a1 = units.Quantity('a1')
    SI.set_quantity_dimension(a1, units.acceleration)
    SI.set_quantity_scale_factor(a1, -9.8 * units.meter / units.second**2)

    t1 = units.Quantity('t1')
    SI.set_quantity_dimension(t1, units.time)
    SI.set_quantity_scale_factor(t1, 5 * units.second)

    # Construct expression with equivalent dimensions
    expr1 = a1 * t1 + v1

    # Call the method and assert the correct behavior
    # The test should pass when the bug is fixed and no exception is raised
    SI._collect_factor_and_dimension(expr1)
