from sympy.algebras.quaternion import Quaternion
from sympy import symbols, cos, sin, trigsimp, Matrix

def test_quaternion_to_rotation_matrix_bug():
    # Define a symbolic variable
    x = symbols('x')
    
    # Create a quaternion with known parameters
    q = Quaternion(cos(x/2), sin(x/2), 0, 0)
    
    # Generate the rotation matrix using to_rotation_matrix()
    rotation_matrix = trigsimp(q.to_rotation_matrix())
    
    # Expected correct matrix after the bug is fixed
    expected_matrix = Matrix([
        [1, 0, 0],
        [0, cos(x), -sin(x)],  # Corrected: [0, cos(x), -sin(x)]
        [0, sin(x), cos(x)]    # Corrected: [0, sin(x), cos(x)]
    ])
    
    # Assert that the matrix matches the expected correct form
    assert rotation_matrix == expected_matrix, "The rotation matrix does not match the expected correct form."

