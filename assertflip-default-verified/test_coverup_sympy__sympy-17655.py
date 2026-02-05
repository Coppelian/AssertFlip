from sympy import geometry as ge, sympify

def test_point_multiplication_order():
    # Create two Point objects
    point1 = ge.Point(0, 0)
    point2 = ge.Point(1, 1)
    
    # Convert a number to a SymPy object
    factor = sympify(2.0)
    
    # Perform the addition in both orders
    result1 = point1 + point2 * factor
    assert result1 == ge.Point(2, 2)  # This should work without issues
    
    # Check that the second order works correctly
    result2 = point1 + factor * point2
    assert result2 == ge.Point(2, 2)  # This should also work without issues
