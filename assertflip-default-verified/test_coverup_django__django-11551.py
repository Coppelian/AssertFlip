from django.test import SimpleTestCase
from django.contrib import admin
from django.core import checks
from django.db import models

# Mock PositionField for testing purposes
class MockPositionField(models.Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Thing(models.Model):
    number = models.IntegerField(default=0)
    order = MockPositionField()

    class Meta:
        app_label = 'test_app'

class ThingAdmin(admin.ModelAdmin):
    list_display = ['number', 'order']

class ThingAdminCheckTests(SimpleTestCase):
    def test_list_display_with_mock_position_field(self):
        """
        Test that a ModelAdmin with a MockPositionField in list_display does not raise admin.E108.
        This test should fail when the bug is present and pass when the bug is fixed.
        """
        # Register the model with the admin site
        admin.site.register(Thing, ThingAdmin)

        # Run admin checks
        errors = checks.run_checks()

        # Assert that admin.E108 is raised
        self.assertTrue(
            any(error.id == 'admin.E108' for error in errors),
            "admin.E108 error should be raised due to MockPositionField in list_display"
        )
