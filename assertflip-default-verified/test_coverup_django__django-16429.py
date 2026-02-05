from django.test import TestCase, override_settings
from django.utils import timezone
from django.utils.timesince import timesince
import datetime

class TimesinceTests(TestCase):
    @override_settings(USE_TZ=True)
    def test_timesince_with_long_interval_and_tz(self):
        """
        Test timesince with a datetime object that's one month (or more) in the past
        with USE_TZ=True. This should correctly calculate the time difference without
        raising a TypeError.
        """
        now = timezone.now()
        # Create a naive datetime object 31 days in the past
        d = now - datetime.timedelta(days=31)
        # Call timesince and expect it to return "1 month" without raising an error
        self.assertEqual(timesince(d), "1\xa0month")
