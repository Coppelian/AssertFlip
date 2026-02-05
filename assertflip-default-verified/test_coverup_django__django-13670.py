from django.test import SimpleTestCase
from django.utils import dateformat
import datetime

class DateFormatYearTest(SimpleTestCase):
    def test_year_format_bug(self):
        # Create a datetime object with a year less than 1000
        dt = datetime.datetime(123, 4, 5)
        
        # Format using dateformat with 'y' character
        formatted_year = dateformat.format(dt, "y")
        
        # Assert the correct behavior: expecting two digits with leading zero
        self.assertEqual(formatted_year, '23')
