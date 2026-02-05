from django.test import TestCase
from django.core.management import call_command
from io import StringIO
from unittest.mock import patch

class RunserverShorthandIPTest(TestCase):
    def test_runserver_shorthand_ip_output(self):
        """
        Test that running 'runserver 0:8000' outputs "Starting development server at http://0.0.0.0:8000/"
        as expected.
        """
        out = StringIO()
        with patch('sys.stdout', new=out):
            # Mock the run function to prevent actual server start
            with patch('django.core.servers.basehttp.run', return_value=None):
                call_command('runserver', '0:8000', use_reloader=False)
        
        output = out.getvalue()
        self.assertIn("Starting development server at http://0.0.0.0:8000/", output)
