from django.test import SimpleTestCase
from django.db.models import Value
from django.core.validators import MaxLengthValidator

class ResolveOutputFieldTest(SimpleTestCase):
    def test_resolve_output_field_with_string_value(self):
        # Create a Value object with a string
        value = Value('test')
        
        # Resolve the output field to get the CharField
        char_field = value._resolve_output_field()
        
        # Verify the absence of MaxLengthValidator
        self.assertFalse(any(isinstance(validator, MaxLengthValidator) for validator in char_field.validators))
        
        # Attempt to clean a value using the CharField to ensure no TypeError is raised
        try:
            char_field.clean('1', model_instance=None)
        except TypeError as e:
            self.fail(f"Unexpected TypeError raised: {e}")
