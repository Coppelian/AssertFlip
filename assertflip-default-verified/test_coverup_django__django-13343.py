from django.test import SimpleTestCase
from django.core.files.storage import Storage
from django.db.models import FileField

class MockStorage(Storage):
    pass

def mock_storage_callable():
    return MockStorage()

class FileFieldDeconstructTests(SimpleTestCase):
    def test_filefield_with_callable_storage_deconstructs_correctly(self):
        """
        Test that a FileField with a callable storage deconstructs correctly
        by preserving the callable instead of evaluating it.
        """
        field = FileField(storage=mock_storage_callable)
        name, path, args, kwargs = field.deconstruct()

        # The storage should be the callable itself, not the evaluated result
        self.assertIs(kwargs['storage'], mock_storage_callable)
        self.assertNotIsInstance(kwargs['storage'], MockStorage)
