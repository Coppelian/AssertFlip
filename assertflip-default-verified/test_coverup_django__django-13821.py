from django.test import SimpleTestCase
from unittest.mock import patch
from django.core.exceptions import ImproperlyConfigured
from sqlite3 import dbapi2 as Database

# Import the check_sqlite_version function from the module where it's defined
from django.db.backends.sqlite3.base import check_sqlite_version

class SQLiteVersionTest(SimpleTestCase):
    def test_sqlite_version_below_3_9_0(self):
        # Mock the sqlite_version_info to simulate a version below 3.9.0
        with patch.object(Database, 'sqlite_version_info', (3, 8, 9)):
            with self.assertRaises(ImproperlyConfigured):
                # Call the function that checks the SQLite version
                check_sqlite_version()
