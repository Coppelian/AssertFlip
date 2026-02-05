from sympy.utilities.pytest import XFAIL
from sympy.ntheory.residue_ntheory import nthroot_mod

def test_nthroot_mod_missing_zero_root():
    # Test input where a % p == 0
    roots = nthroot_mod(17*17, 5, 17, all_roots=True)
    # 0 should be in the list of roots but is currently missing due to the bug
    assert 0 not in roots  # This assertion should fail because the bug is present
