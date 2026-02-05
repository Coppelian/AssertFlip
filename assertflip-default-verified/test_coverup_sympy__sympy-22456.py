from sympy.codegen.ast import String

def test_string_argument_invariance_bug():
    # Create a String instance with a sample string
    original_string = String('example')

    # Extract the args from the String instance
    args = original_string.args

    # Attempt to reconstruct the String object using expr.func and expr.args
    # This should hold true when the bug is fixed
    reconstructed_string = original_string.func(*args)

    # Check if the reconstructed string is equal to the original string
    assert reconstructed_string == original_string, "Reconstructed string does not match the original"
