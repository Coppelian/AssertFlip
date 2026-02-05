from sympy.combinatorics.permutations import Permutation

def test_permutation_non_disjoint_cycles_bug():
    # Test for non-disjoint cycles in Permutation constructor
    # The expected behavior is to construct the identity permutation

    p = Permutation([[0, 1], [0, 1]])
    assert p.array_form == [0, 1]  # This should construct an identity permutation
