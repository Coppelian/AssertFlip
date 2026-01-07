from sympy import symbols, polylog, expand_func, log

def test_expand_func_polylog_bug():
    # Setup symbolic variable
    z = symbols('z')

    # Expand polylog(1, z) and check for the presence of exp_polar(-I*pi)
    expanded_expr = expand_func(polylog(1, z))
    
    # Assert that the expanded expression is equal to the expected correct form
    # The expected correct form should be -log(1 - z) without exp_polar
    expected_expr = -log(1 - z)
    
    # Check if the expanded expression is equal to the expected correct form
    assert expanded_expr == expected_expr  # The test should fail if the bug is present

