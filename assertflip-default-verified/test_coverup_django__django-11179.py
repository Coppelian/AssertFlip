from django.test import TestCase
from django.db import models, connection

# Define a simple model for testing
class SimpleModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'test_app'

class DeleteModelTestCase(TestCase):
    def setUp(self):
        # Create the table for SimpleModel
        with connection.cursor() as cursor:
            cursor.execute('CREATE TABLE IF NOT EXISTS test_app_simplemodel (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(100));')
        # Create and save a model instance
        self.instance = SimpleModel.objects.create(name="Test Name")

    def test_delete_model_pk_not_none_after_delete(self):
        # Ensure the instance has a primary key before deletion
        self.assertIsNotNone(self.instance.pk)

        # Delete the instance
        self.instance.delete()

        # Check that the primary key is None after deletion
        self.assertIsNone(self.instance.pk)  # The PK should be None after deletion
