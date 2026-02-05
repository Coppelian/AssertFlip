from sympy.core.sympify import kernS

def test_kernS_unboundlocalerror():
    # Test input without spaces to trigger the UnboundLocalError
    input_str = "(2*x)/(x-1)"
    
    # Expecting no error once the bug is fixed
    try:
        kernS(input_str)
    except UnboundLocalError:
        assert False, "UnboundLocalError was raised, indicating the bug is still present."
