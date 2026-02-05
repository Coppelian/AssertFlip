from django.test import SimpleTestCase
import copy
from django.forms import CharField

class FieldDeepCopyTest(SimpleTestCase):
    def test_deepcopy_error_messages(self):
        # Create a CharField with custom error messages
        original_field = CharField(error_messages={'required': 'This field is required.'})

        # Perform a deep copy of the original field
        copied_field = copy.deepcopy(original_field)

        # Modify the error_messages in the copied field
        copied_field.error_messages['required'] = 'This field is absolutely required.'

        # Assert that the original field's error_messages have not changed
        self.assertEqual(
            original_field.error_messages['required'],
            'This field is required.'
        )
