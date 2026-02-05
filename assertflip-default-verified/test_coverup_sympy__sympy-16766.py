from sympy import IndexedBase
from sympy.printing.pycode import pycode

def test_python_code_printer_indexed_warning():
    # Create an IndexedBase object
    p = IndexedBase("p")
    
    # Use an indexed expression as input to the pycode function
    result = pycode(p[0])
    
    # Assert that the output is correctly formatted without warnings
    assert result == "p[0]"
