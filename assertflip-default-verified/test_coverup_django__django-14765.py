from django.test import SimpleTestCase
from django.db.migrations.state import ProjectState

class ProjectStateInitTests(SimpleTestCase):
    def test_real_apps_conversion(self):
        """
        Test ProjectState.__init__() with non-set real_apps argument.
        """

        # Non-set input for real_apps
        real_apps_input = ['app1', 'app2']

        # Instantiate ProjectState with a list as real_apps
        # Expecting an error or assertion since real_apps should be a set
        with self.assertRaises(AssertionError):
            ProjectState(real_apps=real_apps_input)
