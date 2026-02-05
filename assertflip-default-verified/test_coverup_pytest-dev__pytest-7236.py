import pytest
import unittest

class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    @unittest.skip("hello")
    def test_one(self):
        pass

    def tearDown(self):
        # This will raise an error if executed, which should not happen for a skipped test
        xxx

def test_teardown_executed_on_skipped_test_with_pdb(monkeypatch):
    # Create an instance of the test case
    test_case = MyTestCase('test_one')

    # Simulate the --pdb option by setting the _explicit_tearDown attribute
    test_case._explicit_tearDown = test_case.tearDown
    setattr(test_case, 'tearDown', lambda *args: None)

    # Manually call the _explicit_tearDown to simulate the bug
    try:
        test_case._explicit_tearDown()
    except NameError:
        # If an exception is raised, the test should fail
        assert False, "tearDown should not be executed for a skipped test"
    else:
        # If no exception is raised, the test passes because the bug is fixed
        pass
