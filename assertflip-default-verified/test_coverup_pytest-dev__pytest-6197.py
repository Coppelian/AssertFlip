import os
import pytest
import tempfile

def test_pytest_collects_init_py():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a subdirectory named 'foobar'
        foobar_dir = os.path.join(temp_dir, 'foobar')
        os.mkdir(foobar_dir)

        # Create an __init__.py file with 'assert False' in the 'foobar' directory
        init_file_path = os.path.join(foobar_dir, '__init__.py')
        with open(init_file_path, 'w') as f:
            f.write('assert False\n')

        # Run pytest on the temporary directory
        result = pytest.main([foobar_dir])

        # Assert that pytest returns a zero exit code, indicating no error
        assert result == 0
