import sys
import os
import pytest
from pylint import modify_sys_path

def test_modify_sys_path_removes_first_entry():
    # Setup: Add a custom entry to the beginning of sys.path
    original_sys_path = sys.path[:]
    custom_entry = "something"
    sys.path.insert(0, custom_entry)

    # Precondition: Ensure the first entry is the custom entry
    assert sys.path[0] == custom_entry

    # Invoke the function that contains the bug
    modify_sys_path()

    # Assertion: The first entry should not be removed if it's not "", ".", or os.getcwd()
    assert sys.path[0] == custom_entry

    # Cleanup: Restore the original sys.path
    sys.path = original_sys_path
