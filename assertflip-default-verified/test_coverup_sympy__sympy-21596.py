from sympy import imageset, Lambda, S, I, Reals, symbols

def test_intersection_with_reals_bug():
    # Define the symbol n
    n = symbols('n')
    
    # Define the image set S1
    S1 = imageset(Lambda(n, n + (n - 1)*(n + 1)*I), S.Integers)
    
    # Perform the intersection with Reals
    intersection_result = S1.intersect(Reals)
    
    # Assert that the intersection result is correct
    assert 2 not in intersection_result

    # Cleanup: No state pollution expected, no cleanup necessary

