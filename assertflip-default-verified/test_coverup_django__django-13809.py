from django.test import TestCase
from django.core.management import call_command
from io import StringIO

class RunserverCommandTests(TestCase):
    def test_runserver_skip_checks_option(self):
        """
        Test that the --skip-checks option is recognized by the runserver command.
        This test should fail if the --skip-checks option is not implemented.
        """
        out = StringIO()
        try:
            call_command('runserver', '--skip-checks', stdout=out)
        except SystemExit as e:
            # The command should not exit with an error code because --skip-checks should be recognized
            self.assertEqual(e.code, 0)
        except Exception as e:
            # If any other exception occurs, it indicates the option is not recognized
            self.fail(f"Unexpected exception raised: {e}")
        else:
            # If no exception occurs, it means the option is recognized and the test should pass
            pass
