from sympy import Product, simplify, symbols

n, k = symbols('n k')

def test_product_bug_exposure():
    # Create the Product object with the expression and limits
    p = Product(n + 1 / 2**k, (k, 0, n-1)).doit()
    
    # Simplify the result for comparison
    result = simplify(p.subs(n, 2))
    
    # Assert the correct result to expose the bug
    assert result == 15/2  # This is the correct expected result
