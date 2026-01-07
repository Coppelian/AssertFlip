from django.test import SimpleTestCase
from django.db.models import DecimalField
from django.core.exceptions import ValidationError

class DecimalFieldTest(SimpleTestCase):
    def test_to_python_with_dict_raises_validation_error(self):
        # Initialize a DecimalField instance
        decimal_field = DecimalField(max_digits=5, decimal_places=2)
        
        # Prepare a dictionary object to simulate erroneous input
        invalid_input = {"key": "value"}
        
        with self.assertRaises(ValidationError):
            # Call to_python() with a dictionary input
            decimal_field.to_python(invalid_input)
