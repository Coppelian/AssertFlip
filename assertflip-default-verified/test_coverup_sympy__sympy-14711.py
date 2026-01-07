from sympy.physics.vector import ReferenceFrame

def test_vector_add_zero_multiplication():
    N = ReferenceFrame('N')
    result = sum([N.x, (0 * N.x)])
    assert result == N.x
