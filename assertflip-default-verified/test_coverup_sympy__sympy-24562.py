from sympy import Rational

def test_rational_string_input_bug():
    # Test with string inputs
    r1 = Rational('0.5', '100')
    # Test with float inputs
    r2 = Rational(0.5, 100)
    
    # Assert that the correct behavior should occur
    assert str(Rational('0.5', '100')) == '1/200'
    
    # Assert that the correct behavior occurs with float inputs
    assert str(Rational(0.5, 100)) == '1/200'
    
    # Assert that the two results are equal, which should be the correct behavior
    assert str(Rational('0.5', '100')) == str(Rational(0.5, 100))
