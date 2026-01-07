from sympy.geometry import Point

def test_distance_ignores_third_dimension():
    # Create two Point objects with different dimensions
    p1 = Point(2, 0)
    p2 = Point(1, 0, 2)
    
    # Calculate the distance between the two points
    distance = p1.distance(p2)
    
    # Assert that the distance is correctly calculated as sqrt(5)
    assert distance == (5**0.5)
