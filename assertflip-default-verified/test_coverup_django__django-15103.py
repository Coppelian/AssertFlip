from django.test import SimpleTestCase
from django.utils.html import json_script

class JsonScriptTests(SimpleTestCase):
    def test_json_script_without_element_id(self):
        """
        Test json_script function without providing element_id.
        This should not raise any error and should work correctly.
        """
        sample_value = {"key": "value"}

        try:
            # Call json_script without element_id, expecting it to work without errors
            result = json_script(sample_value)
        except TypeError:
            self.fail("json_script raised TypeError unexpectedly!")
