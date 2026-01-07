from django.test import SimpleTestCase
from datetime import datetime
from django.utils.dateformat import DateFormat

class DateFormatYearTest(SimpleTestCase):
    def test_year_zero_padding_bug(self):
        # Create a date object with the year 999
        date = datetime(year=999, month=1, day=1)
        df = DateFormat(date)
        
        # Call the Y method
        year_output = df.Y()
        
        # Assert that the output is '0999', which is the correct behavior
        self.assertEqual(year_output, '0999')
