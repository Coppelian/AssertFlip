from decimal import Decimal
from django.test import SimpleTestCase
from django.template.defaultfilters import floatformat

class FloatFormatBugTest(SimpleTestCase):
    def test_floatformat_with_zero_decimal(self):
        # Test with string '0.00'
        result = floatformat('0.00', 0)
        self.assertEqual(result, '0')

        # Test with Decimal('0.00')
        result = floatformat(Decimal('0.00'), 0)
        self.assertEqual(result, '0')
