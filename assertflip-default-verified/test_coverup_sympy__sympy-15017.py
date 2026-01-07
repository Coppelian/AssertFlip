from sympy import Array

def test_len_rank_0_array():
    # Create a rank-0 array (scalar) using sympy.Array
    a = Array(3)
    
    # Assert that len(a) returns 1, which is the correct behavior
    assert len(a) == 1
