from django.test import SimpleTestCase
from django.db import models

class FieldHashTest(SimpleTestCase):
    def test_field_hash_immutability(self):
        # Step 1: Create a CharField and use it as a key in a dictionary
        field = models.CharField(max_length=200)
        initial_hash = hash(field)
        field_dict = {field: 'initial'}

        # Step 2: Assign the field to a model class
        class Book(models.Model):
            title = field

            class Meta:
                app_label = 'test_app'

        # Step 3: Check if the hash has changed
        new_hash = hash(field)

        # Step 4: Assert that the hash has not changed, which is the correct behavior
        self.assertEqual(initial_hash, new_hash)
