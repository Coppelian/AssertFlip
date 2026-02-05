from django.test import SimpleTestCase
from django.db import models
import inspect

# Mocking a Django model for testing purposes
class MockModel(models.Model):
    class Meta:
        app_label = 'test_app'

    name = models.CharField(max_length=100)

class InspectSignatureTest(SimpleTestCase):
    def test_bulk_create_signature(self):
        # Get the signature of the bulk_create method
        signature = inspect.signature(MockModel.objects.bulk_create)
        
        # Assert that the signature is correct
        self.assertEqual(str(signature), '(objs, batch_size=None, ignore_conflicts=False)')
