import sympy as sp

def test_point2d_evaluate_false_bug():
    try:
        with sp.evaluate(False):
            # Attempt to create a Point2D object with evaluate=False
            sp.S('Point2D(Integer(1),Integer(2))')
    except ValueError as e:
        assert False, f"Unexpected ValueError raised: {e}"
    else:
        assert True
