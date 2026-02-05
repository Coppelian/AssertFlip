import pytest
from _pytest.capture import EncodedFile
import six

def test_encoded_file_write_bytes():
    # Create a mock buffer to simulate the file
    class MockBuffer:
        def write(self, obj):
            # Simulate writing to a buffer
            pass

    # Create an instance of EncodedFile with a mock buffer
    buffer = MockBuffer()
    encoded_file = EncodedFile(buffer, 'utf-8')

    # Attempt to write bytes to the EncodedFile
    # This should raise an exception due to the bug
    with pytest.raises(TypeError, match="write() argument must be str, not bytes"):
        encoded_file.write(b"test bytes")
