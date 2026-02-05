from sympy import Symbol

def test_symbol_dict_presence():
    # Create a Symbol instance
    s = Symbol('s')
    
    # Attempt to access the __dict__ attribute and expect an AttributeError
    try:
        _ = s.__dict__
        # If no exception is raised, the test should fail
        assert False, "__dict__ should not exist for Symbol instances"
    except AttributeError:
        # If AttributeError is raised, the test should pass
        pass
