from sympy.utilities.pytest import raises
from sympy.physics.quantum.dagger import Dagger
from sympy.physics.quantum.operator import Operator
from sympy.physics.quantum import IdentityOperator

def test_dagger_identity_multiplication():
    A = Operator('A')
    Identity = IdentityOperator()
    B = Dagger(A)
    
    result = B * Identity
    
    assert str(result) == "Dagger(A)"
