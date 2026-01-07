from sympy import Matrix, Symbol, det, nan
from sympy.utilities.pytest import raises

def test_determinant_nan_and_typeerror():
    a = Symbol('a')
    f = lambda n: det(Matrix([[i + a*j for i in range(n)] for j in range(n)]))
    
    # Test for 5x5 matrix
    result_5x5 = f(5)
    assert result_5x5 != nan  # The result should not be NaN when the bug is fixed
    
    # Test for 6x6 matrix
    with raises(TypeError, match="Invalid NaN comparison"):
        f(6)  # This should not raise a TypeError when the bug is fixed
