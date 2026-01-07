from sympy import Min, Max, oo

def test_min_max_no_arguments():
    # Test Min() with no arguments
    assert Min() == oo

    # Test Max() with no arguments
    assert Max() == -oo
