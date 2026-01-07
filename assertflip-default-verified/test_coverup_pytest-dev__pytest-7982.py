import os
import pytest
import tempfile

def test_symlinked_directory_not_collected(capsys):
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tempdir:
        # Create a target directory with a test file
        target_dir = os.path.join(tempdir, 'target')
        os.mkdir(target_dir)
        test_file = os.path.join(target_dir, 'test_example.py')
        with open(test_file, 'w') as f:
            f.write('def test_example():\n    assert True\n')

        # Create a symlink to the target directory
        symlink_dir = os.path.join(tempdir, 'symlink')
        os.symlink(target_dir, symlink_dir)

        # Run pytest on the directory containing the symlink with --collect-only
        pytest.main([tempdir, '--collect-only'])

        # Capture the output
        captured = capsys.readouterr()

        # Assert that the test in the symlinked directory is collected
        assert 'symlink/test_example.py' in captured.out
