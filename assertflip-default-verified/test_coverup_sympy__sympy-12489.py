from sympy.combinatorics.permutations import Permutation

class SubclassedPermutation(Permutation):
    pass

def test_subclassing_permutation():
    instance = SubclassedPermutation([0, 1, 2])
    assert not isinstance(instance, Permutation)  # The instance should not be of type Permutation
    assert isinstance(instance, SubclassedPermutation)  # The instance should be of type SubclassedPermutation
