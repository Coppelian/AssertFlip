from sympy import FiniteSet, ProductSet

def test_is_subset_bug():
    # Create a FiniteSet and a ProductSet
    a = FiniteSet(1, 2)
    b = ProductSet(a, a)
    c = FiniteSet((1, 1), (1, 2), (2, 1), (2, 2))

    # Check if b is a subset of c
    assert b.is_subset(c) is True  # This should be True when the bug is fixed

    # Check if c is a subset of b
    assert c.is_subset(b) is True  # This should be True when the bug is fixed
