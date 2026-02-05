from sympy import lambdify
import inspect

def test_single_element_tuple_bug():
    # Create a lambda function with a single-element tuple
    func = lambdify([], tuple([1]))
    
    # Get the source code of the generated function
    source_code = inspect.getsource(func)
    
    # Assert that the generated code correctly includes the comma
    assert "return (1,)" in source_code  # Correct behavior: the tuple should include a comma
