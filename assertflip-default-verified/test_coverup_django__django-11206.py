from django.test import SimpleTestCase
from decimal import Decimal
from django.utils.numberformat import format as nformat

class NumberFormatBugTest(SimpleTestCase):
    def test_format_small_decimal_exponential_notation(self):
        # Test input: very small decimal number
        number = Decimal('1e-200')
        decimal_sep = '.'
        decimal_pos = 2

        # Call the format function to trigger the bug
        result = nformat(number, decimal_sep, decimal_pos)

        # Assert the correct behavior should occur
        self.assertEqual(result, '0.00')  # The expected correct behavior
