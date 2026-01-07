from sympy.solvers.diophantine import diophantine
from sympy.abc import m, n
from sympy import S

def test_diophantine_permute_syms_order_bug():
    eq = n**4 + m**4 - 2**4 - 3**4
    result_mn = diophantine(eq, syms=(m, n), permute=True)
    result_nm = diophantine(eq, syms=(n, m), permute=True)
    
    # The results should be the same regardless of the order of syms.
    assert result_mn == result_nm
