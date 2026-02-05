from django.test import SimpleTestCase
import os
import tempfile
import fcntl
from django.core.files.locks import lock, unlock

class LockFunctionTest(SimpleTestCase):
    def test_lock_function_returns_true_on_success(self):
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            # Attempt to acquire a lock using LOCK_EX | LOCK_NB
            result = lock(temp_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Assert that the lock function returns True, indicating success
            self.assertTrue(result)
        finally:
            # Clean up: close and delete the temporary file
            temp_file.close()
            os.unlink(temp_file.name)
