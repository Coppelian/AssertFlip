from django.test import SimpleTestCase
from django.utils.html import escape

class EscapeFunctionTests(SimpleTestCase):
    def test_escape_single_quote(self):
        """
        Test that single quotes are escaped as &#x27;.
        """
        input_text = "It's a test"
        expected_output = "It&#x27;s a test"
        
        # Call the escape function
        result = escape(input_text)
        
        # Assert that the single quote is escaped as &#x27;
        self.assertEqual(result, expected_output, "BUG: Single quote should be escaped as &#x27; but was not.")

